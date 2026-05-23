from pathlib import Path
from typing import Optional

import typer

from cpho_cli.core.config import ConfigError
from cpho_cli.core.eval import EvalConfigError, run_eval
from cpho_cli.core.index import IndexBuildError, OcrUpgradeDecisionRequired, build_index, list_pending_candidates
from cpho_cli.core.solve import SolveError, solve_problem

app = typer.Typer(help="CPHO local physics analysis CLI.")

_OCR_STRATEGY_CHOICES = ("prompt", "reuse", "rebuild", "new-only")


@app.command()
def solve(
    problem: Path = typer.Argument(..., help="Problem PDF or image path."),
    answer: Optional[Path] = typer.Option(None, "--answer", "-a", help="Answer key path."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Local YAML config path."),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="Provider profile name from config."
    ),
    output_dir: Path = typer.Option(Path("output"), "--output-dir", "-o", help="Output directory."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate inputs without LLM calls."),
) -> None:
    """Solve one physics problem."""
    try:
        result = solve_problem(
            problem,
            answer_path=answer,
            config_path=config,
            provider_name=provider,
            output_dir=output_dir,
            dry_run=dry_run,
        )
    except (ConfigError, SolveError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    if result.report_json is None:
        typer.echo("Dry run passed.")
        return
    typer.echo(f"Report JSON: {result.report_json}")
    if result.report_markdown is not None:
        typer.echo(f"Report Markdown: {result.report_markdown}")


@app.command(name="eval")
def eval_command(
    golden_root: Path = typer.Argument(..., help="Golden tests root directory."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Local YAML config path."),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="Provider profile name from config."
    ),
    output_dir: Path = typer.Option(
        Path("eval-output"), "--output-dir", "-o", help="Evaluation output directory."
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate cases without LLM calls."),
) -> None:
    """Run golden evaluation cases."""
    try:
        result = run_eval(
            golden_root,
            config_path=config,
            provider_name=provider,
            output_dir=output_dir,
            dry_run=dry_run,
        )
    except EvalConfigError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(
        f"Evaluation complete: total={result.total} passed={result.passed} "
        f"failed={result.failed} skipped={result.skipped}"
    )


@app.command(name="index")
def index_command(
    workspace: Path = typer.Argument(Path.cwd(), help="工作空间目录（默认: 当前目录）。"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="本地 YAML 配置文件路径。"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="配置中的 provider 名称。"),
    force: bool = typer.Option(False, "--force", help="强制重建全部索引，忽略 fingerprint。"),
    only_new: bool = typer.Option(False, "--only-new", help="仅索引新增题目，跳过已存在条目。"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅验证 workspace 与词表，不调用 LLM 不写文件。"),
    ocr_strategy: str = typer.Option("prompt", "--ocr-strategy", help="OCR 引擎升级策略: prompt|reuse|rebuild|new-only"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="仅输出错误。"),
    list_candidates_flag: bool = typer.Option(False, "--list-candidates", help="只列出 pending candidate tag，不重建索引。"),
) -> None:
    """对工作空间题目生成结构化索引。"""
    if ocr_strategy not in _OCR_STRATEGY_CHOICES:
        raise typer.BadParameter(
            f"--ocr-strategy must be one of {_OCR_STRATEGY_CHOICES}; got {ocr_strategy!r}"
        )

    if list_candidates_flag:
        candidates = list_pending_candidates(workspace)
        if not candidates:
            typer.echo("无待审候选标签。")
            return
        for c in candidates:
            typer.echo(f"  {c.display_zh_suggestion} ({c.internal_id_suggestion}) x{c.occurrences}")
        return

    try:
        stats = build_index(
            workspace,
            config_path=config,
            provider_name=provider,
            force=force,
            only_new=only_new,
            dry_run=dry_run,
            ocr_strategy=ocr_strategy,
        )
    except OcrUpgradeDecisionRequired as exc:
        delta = exc.delta
        typer.echo(delta.summary())
        typer.echo("受影响条目: " + str(delta.affected_count))
        typer.echo("")
        typer.echo("请选择:")
        typer.echo("  [a] 重建全部")
        typer.echo("  [b] 仅重建受影响条目")
        typer.echo("  [c] 暂时跳过，保持现有 OCR")
        typer.echo("  [d] 仅索引新增题目，不动旧条目")
        choice = typer.prompt("选择 [a/b/c/d]").strip().lower()
        mapping = {"a": ("rebuild", True), "b": ("rebuild", False), "c": ("reuse", False), "d": ("new-only", False)}
        if choice not in mapping:
            raise typer.BadParameter(f"无效选择: {choice}; 应为 a|b|c|d") from None
        new_strategy, new_force = mapping[choice]
        try:
            stats = build_index(
                workspace,
                config_path=config,
                provider_name=provider,
                force=force or new_force,
                only_new=only_new,
                dry_run=dry_run,
                ocr_strategy=new_strategy,
            )
        except (ConfigError, IndexBuildError) as inner_exc:
            raise typer.BadParameter(str(inner_exc)) from inner_exc
    except (ConfigError, IndexBuildError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    if not quiet:
        typer.echo(f"索引统计 (workspace: {workspace})")
        typer.echo("─────────────────────────")
        typer.echo(f"扫描题目数:        {stats.total_problems}")
        typer.echo(f"  文件变化:        {stats.file_changed}")
        typer.echo(f"  无变化:          {stats.file_unchanged}")
        typer.echo("")
        typer.echo(f"OCR 复用:          {stats.ocr_reused}")
        typer.echo(f"OCR 重生成:        {stats.ocr_regenerated}")
        typer.echo(f"OCR 引擎升级:      {'已处理' if stats.ocr_engine_upgrade_detected else '未检测到'}")
        if stats.forced_regenerations > 0:
            typer.echo(f"强制重建:          {stats.forced_regenerations}  (--force 触发, 内容未变)")
        typer.echo("")
        typer.echo("标签层:")
        typer.echo(f"  重新生成:        {stats.tags_regenerated}")
        typer.echo(f"  跳过 (fingerprint): {stats.tags_skipped}")
        typer.echo(f"  精炼层 (用户笔记):  {stats.refinement_only}")
        typer.echo("")
        typer.echo("候选词表:")
        typer.echo(f"  本次新提议:      {stats.candidate_tags_proposed}")
        typer.echo(f"  累计待审:        {stats.pending_review_items}  (运行 `cpho index --list-candidates` 查看)")
        typer.echo("")
        typer.echo(f"完成. 索引: {workspace}/.cpho/index.jsonl")
