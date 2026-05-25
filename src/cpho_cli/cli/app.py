from pathlib import Path
from typing import Optional

import click
import typer

from cpho_cli.core.config import ConfigError
from cpho_cli.core.eval import EvalConfigError, run_eval
from cpho_cli.core.index import (
    add_problem_tags,
    IndexBuildError,
    IndexNotFoundError,
    OcrUpgradeDecisionRequired,
    VocabularyError,
    build_index,
    list_pending_candidates,
    remove_problem_tags,
    update_problem_tags,
)
from cpho_cli.core.solve import SolveError, solve_problem

app = typer.Typer(help="CPHO local physics analysis CLI.")
topic_app = typer.Typer(help="主题分类浏览。")


class IndexGroup(typer.core.TyperGroup):
    def resolve_command(self, ctx: click.Context, args: list[str]):
        if args and not args[0].startswith("-") and args[0] not in self.commands:
            return super().resolve_command(ctx, ["build", *args])
        return super().resolve_command(ctx, args)


index_app = typer.Typer(
    help="题目索引构建与标签读写。",
    cls=IndexGroup,
    invoke_without_command=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
app.add_typer(topic_app, name="topic")
app.add_typer(index_app, name="index")

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


def _index_progress_cli(event: dict) -> None:
    phase = event.get("phase", "")
    if phase == "begin":
        typer.echo(f"开始索引: {event['total_files']} 个文件")
    elif phase == "paper_split_start":
        typer.echo(f"  切分 [{event['file_index']}/{event['total_files']}]: {event['file_path'][-60:]}")
    elif phase == "problem_tag_done":
        typer.echo(
            f"  [{event['problem_id']}]: "
            f"物理={event['physics_count']} 数学={event['math_count']} 启发={event['heuristic_count']}"
        )
    elif phase == "problem_skip":
        typer.echo(f"  跳过 [{event['problem_id']}]: 无变化")


@index_app.callback(invoke_without_command=True)
def index_command(
    ctx: typer.Context,
    workspace_option: Optional[Path] = typer.Option(
        None,
        "--workspace",
        "-w",
        help="工作空间目录（默认: 当前目录；也可作为位置参数传入）。",
    ),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="本地 YAML 配置文件路径。"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="配置中的 provider 名称。"),
    force: bool = typer.Option(False, "--force", help="强制重建全部索引，忽略 fingerprint。"),
    force_all: bool = typer.Option(False, "--force-all", help="强制完全重建，并清空 skill/用户写入标签。"),
    only_new: bool = typer.Option(False, "--only-new", help="仅索引新增题目，跳过已存在条目。"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅验证 workspace 与词表，不调用 LLM 不写文件。"),
    ocr_strategy: str = typer.Option("prompt", "--ocr-strategy", help="OCR 引擎升级策略: prompt|reuse|rebuild|new-only"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="仅输出错误。"),
    list_candidates_flag: bool = typer.Option(False, "--list-candidates", help="只列出 pending candidate tag，不重建索引。"),
) -> None:
    """对工作空间题目生成结构化索引。"""
    if ctx.invoked_subcommand is not None:
        return
    extra_args = list(ctx.args)
    if workspace_option is not None and extra_args:
        raise typer.BadParameter("工作空间不能同时用位置参数和 --workspace 指定。")
    if len(extra_args) > 1:
        raise typer.BadParameter(f"未知参数: {' '.join(extra_args[1:])}")
    workspace = workspace_option or (Path(extra_args[0]) if extra_args else Path.cwd())

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
            force_all=force_all,
            only_new=only_new,
            dry_run=dry_run,
            ocr_strategy=ocr_strategy,
            on_progress=_index_progress_cli if not quiet else None,
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
                force_all=force_all,
                only_new=only_new,
                dry_run=dry_run,
                ocr_strategy=new_strategy,
                on_progress=_index_progress_cli if not quiet else None,
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
        typer.echo("试卷切分:")
        typer.echo(f"  切分试卷数:      {stats.papers_split}")
        typer.echo(f"  提取题目数:      {stats.problems_extracted}")
        typer.echo(f"  规则切分:        {stats.split_method_rules}")
        typer.echo(f"  LLM 切分:        {stats.split_method_llm}")
        typer.echo(f"  单题路径:        {stats.split_method_single}")
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


class _IndexBuildContext:
    invoked_subcommand = None

    def __init__(self, workspace: Path) -> None:
        self.args = [str(workspace)]


@index_app.command(name="build", hidden=True)
def index_build_command(
    workspace: Path = typer.Argument(Path.cwd(), help="工作空间目录（默认: 当前目录）。"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="本地 YAML 配置文件路径。"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="配置中的 provider 名称。"),
    force: bool = typer.Option(False, "--force", help="强制重建全部索引，忽略 fingerprint。"),
    force_all: bool = typer.Option(False, "--force-all", help="强制完全重建，并清空 skill/用户写入标签。"),
    only_new: bool = typer.Option(False, "--only-new", help="仅索引新增题目，跳过已存在条目。"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅验证 workspace 与词表，不调用 LLM 不写文件。"),
    ocr_strategy: str = typer.Option("prompt", "--ocr-strategy", help="OCR 引擎升级策略: prompt|reuse|rebuild|new-only"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="仅输出错误。"),
    list_candidates_flag: bool = typer.Option(False, "--list-candidates", help="只列出 pending candidate tag，不重建索引。"),
) -> None:
    index_command(
        _IndexBuildContext(workspace),  # type: ignore[arg-type]
        workspace_option=None,
        config=config,
        provider=provider,
        force=force,
        force_all=force_all,
        only_new=only_new,
        dry_run=dry_run,
        ocr_strategy=ocr_strategy,
        quiet=quiet,
        list_candidates_flag=list_candidates_flag,
    )


def _require_tags(tags: list[str]) -> list[str]:
    if not tags:
        raise typer.BadParameter("至少提供一个 --tag/-t。")
    return tags


@index_app.command(name="tag-add")
def index_tag_add(
    workspace: Path = typer.Option(Path.cwd(), "--workspace", "-w", help="工作空间目录。"),
    problem_id: str = typer.Option(..., "--problem-id", help="题目 ID。"),
    tags: list[str] = typer.Option([], "--tag", "-t", help="要追加的标签，可重复。"),
    skill_name: str = typer.Option(..., "--skill-name", help="写入标签的 skill 名称。"),
    reasoning: str = typer.Option(..., "--reasoning", help="写入依据。"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="仅输出错误。"),
) -> None:
    """追加 skill/用户标签。"""
    try:
        entry = add_problem_tags(
            workspace,
            problem_id,
            _require_tags(tags),
            skill_name=skill_name,
            reasoning=reasoning,
        )
    except IndexBuildError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if not quiet:
        typer.echo(f"已追加标签: {entry.problem_id} ({len(tags)} 个)")


@index_app.command(name="tag-remove")
def index_tag_remove(
    workspace: Path = typer.Option(Path.cwd(), "--workspace", "-w", help="工作空间目录。"),
    problem_id: str = typer.Option(..., "--problem-id", help="题目 ID。"),
    tags: list[str] = typer.Option([], "--tag", "-t", help="要移除的标签，可重复。"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="仅输出错误。"),
) -> None:
    """移除 skill/用户标签。"""
    try:
        entry = remove_problem_tags(workspace, problem_id, _require_tags(tags))
    except IndexBuildError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if not quiet:
        typer.echo(f"已移除标签: {entry.problem_id} ({len(tags)} 个)")


@index_app.command(name="tag-set")
def index_tag_set(
    workspace: Path = typer.Option(Path.cwd(), "--workspace", "-w", help="工作空间目录。"),
    problem_id: str = typer.Option(..., "--problem-id", help="题目 ID。"),
    tags: list[str] = typer.Option([], "--tag", "-t", help="新的完整标签集合，可重复。"),
    skill_name: str = typer.Option(..., "--skill-name", help="写入标签的 skill 名称。"),
    reasoning: str = typer.Option(..., "--reasoning", help="写入依据。"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="仅输出错误。"),
) -> None:
    """替换 skill/用户标签集合。"""
    try:
        entry = update_problem_tags(
            workspace,
            problem_id,
            _require_tags(tags),
            skill_name=skill_name,
            reasoning=reasoning,
        )
    except IndexBuildError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if not quiet:
        typer.echo(f"已设置标签: {entry.problem_id} ({len(tags)} 个)")


def _print_tree(nodes: list, level: int = 0) -> None:  # type: ignore[type-arg]
    for node in nodes:
        indent = "  " * level
        typer.echo(f"{indent}{node.display_zh} ({node.id})")
        _print_tree(node.children, level + 1)


@topic_app.command(name="list")
def topic_list(
    workspace: Path = typer.Argument(Path.cwd(), help="Workspace 目录."),
) -> None:
    """显示完整主题分类树。"""
    from cpho_cli.core.index.topic_vocabulary import load_merged_topic_taxonomy

    try:
        taxonomy = load_merged_topic_taxonomy(workspace)
    except VocabularyError as exc:
        raise typer.BadParameter(str(exc)) from exc
    _print_tree(taxonomy.roots)


@topic_app.command(name="browse")
def topic_browse(
    path: str = typer.Argument(..., help="主题路径 (如 力学/天体运动)."),
    workspace: Path = typer.Argument(Path.cwd(), help="Workspace 目录."),
) -> None:
    """按主题路径浏览题目。"""
    from cpho_cli.core.index import find_problems_by_topic

    try:
        results = find_problems_by_topic(workspace, path)
    except IndexNotFoundError as exc:
        raise typer.BadParameter(str(exc)) from exc
    for result in results:
        typer.echo(f"  {result.problem_id}: {result.topic_path}")
    typer.echo(f"\n共 {len(results)} 道题目")


@app.command(name="compose")
def compose_command(
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="主题路径前缀 (如 力学/天体运动)."),
    tags: Optional[str] = typer.Option(None, "--tags", help="标签 ID 列表, 逗号分隔."),
    workspace: Path = typer.Argument(Path.cwd(), help="Workspace 目录."),
) -> None:
    """按主题和标签组合筛选题目（组卷）。"""
    from cpho_cli.core.index.compose import compose_problem_list

    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    try:
        results = compose_problem_list(workspace, topic_path=topic, tag_ids=tag_list)
    except (IndexNotFoundError, VocabularyError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    if not results:
        typer.echo("未找到匹配题目。")
        return

    typer.echo(f"组卷结果 ({len(results)} 道题目):")
    for result in results:
        all_tags = ", ".join(
            ref.internal_id
            for ref in result.physics_model_tags
            + result.math_technique_tags
            + result.heuristic_tags
        )
        typer.echo(
            f"  [{result.problem_id}] {result.topic_path or '未分类'} | tags: {all_tags}"
        )


@app.command(name="repl")
def repl_command(
    workspace: Optional[Path] = typer.Option(
        None, "--workspace", "-w", help="工作空间目录（覆盖持久化的 last_workspace）。"
    ),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="本地 YAML 配置文件路径。"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="配置中的 provider 名称。"),
) -> None:
    """启动交互式 REPL（prompt_toolkit）。"""
    import asyncio

    from cpho_cli.cli.repl.app import run_repl

    asyncio.run(run_repl(workspace=workspace, config_path=config, provider_name=provider))
