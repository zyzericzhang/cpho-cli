version: "v0.1"
tags:
  - internal_id: pion_decay_kinematics
    display_zh: π介子衰变运动学
    category: physics_model
    aliases: ["π衰变", "pion decay"]
    description: 用二体衰变能动守恒求μ子和中微子运动学。

  - internal_id: lifetime_time_dilation
    display_zh: 寿命时间膨胀
    category: physics_law
    aliases: ["运动寿命延长", "lifetime dilation"]
    description: 用固有寿命和γ因子计算高速粒子飞行距离。

  - internal_id: decay_product_angle_limit
    display_zh: 衰变角限
    category: heuristic
    aliases: ["最大出射角", "decay angle limit"]
    description: 通过换系和速度合成确定衰变产物角度范围。

  - internal_id: neutrino_energy_angle_relation
    display_zh: 中微子能角关系
    category: physics_law
    aliases: ["能量-角度关系", "neutrino angle-energy"]
    description: 建立实验室系中微子能量与出射角的函数关系。

  - internal_id: two_body_decay_frame
    display_zh: 二体衰变系
    category: heuristic
    aliases: ["母粒子静止系", "two-body rest frame"]
    description: 先在母粒子静止系求末态再变换到实验系。

  - internal_id: annihilation_photon_pair
    display_zh: 双光子湮灭
    category: physics_model
    aliases: ["电子正电子湮灭", "two-photon annihilation"]
    description: 用四动量守恒处理电子正电子湮灭成两光子。

  - internal_id: identical_particle_collision
    display_zh: 同种粒子碰撞
    category: physics_model
    aliases: ["电子电子碰撞", "identical collision"]
    description: 利用对称性处理同质量粒子的相对论碰撞。

  - internal_id: lab_to_com_collision
    display_zh: 碰撞质心化
    category: heuristic
    aliases: ["转质心系碰撞", "COM collision"]
    description: 将实验室系碰撞转入质心系简化动量角度关系。

  - internal_id: photon_energy_extrema
    display_zh: 光子能量极值
    category: math_technique
    aliases: ["能量最大最小", "energy extrema"]
    description: 由出射方向或角变量求光子能量上下界。

  - internal_id: relativistic_doppler_shift
    display_zh: 相对论多普勒
    category: physics_law
    aliases: ["相对论频移", "relativistic Doppler"]
    description: 同时考虑时间膨胀和相对运动导致的频率改变。

  - internal_id: transverse_doppler_effect
    display_zh: 横向多普勒效应
    category: physics_law
    aliases: ["横向频移", "transverse Doppler"]
    description: 垂直视线方向运动也因钟慢产生频率偏移。

  - internal_id: doppler_angle_transform
    display_zh: 多普勒角变换
    category: physics_law
    aliases: ["频率角变换", "Doppler angle"]
    description: 联立光行差与频率变换处理任意方向多普勒。

  - internal_id: four_wavevector_transform
    display_zh: 波矢四矢量
    category: physics_law
    aliases: ["四维波矢", "four-wavevector"]
    description: 将光频率与波矢作为四矢量统一变换。

  - internal_id: photon_four_momentum
    display_zh: 光子四动量
    category: physics_law
    aliases: ["光子能动量", "photon four-momentum"]
    description: 用光子能量和动量组成零质量四动量。

  - internal_id: lorentz_invariant_interval
    display_zh: 时空间隔不变
    category: physics_law
    aliases: ["线元不变", "spacetime interval"]
    description: 用四维间隔不变量推导钟慢和洛伦兹变换。

  - internal_id: null_geodesic_condition
    display_zh: 零测地线条件
    category: physics_law
    aliases: ["光线线元为零", "null geodesic"]
    description: 光子轨迹满足时空间隔为零的测地线条件。

  - internal_id: affine_parameter_elimination
    display_zh: 仿射参量消去
    category: math_technique
    aliases: ["消去λ", "affine parameter"]
    description: 消去测地线参数得到光子轨道微分方程。

  - internal_id: successive_approximation
    display_zh: 逐次逼近法
    category: math_technique
    aliases: ["迭代近似", "successive approximation"]
    description: 将零级解代回方程右端求一级修正解。

  - internal_id: lorenz_gauge_potential
    display_zh: 洛伦兹规范势
    category: physics_law
    aliases: ["Lorenz gauge", "四维势规范"]
    description: 在洛伦兹规范下使用标势和矢势描述辐射场。

  - internal_id: retarded_potential
    display_zh: 推迟势
    category: physics_law
    aliases: ["延迟势", "retarded potential"]
    description: 用源在推迟时刻的运动状态确定电磁势。

  - internal_id: far_field_radiation
    display_zh: 远场辐射项
    category: approximation
    aliases: ["1/r辐射项", "far-field term"]
    description: 保留随距离按1/r衰减的辐射场主导项。

  - internal_id: lienard_radiation_formula
    display_zh: 李纳辐射公式
    category: physics_law
    aliases: ["Liénard formula", "相对论辐射功率"]
    description: 给出任意速度带电粒子加速辐射的总功率。

  - internal_id: oscillator_frequency_shift
    display_zh: 振子频率修正
    category: approximation
    aliases: ["相对论周期修正", "frequency shift"]
    description: 由相对论动能修正简谐振子的周期或频率。

  - internal_id: slow_amplitude_evolution
    display_zh: 缓变振幅法
    category: approximation
    aliases: ["慢变振幅", "adiabatic amplitude"]
    description: 将辐射耗能转化为振幅随时间缓慢衰减。

  - internal_id: radiation_power_average
    display_zh: 辐射功率平均
    category: math_technique
    aliases: ["周期平均功率", "power averaging"]
    description: 对振动周期内辐射功率取平均求能量损失率。

  - internal_id: relativistic_box_pressure
    display_zh: 相对论盒压
    category: physics_model
    aliases: ["粒子盒压强", "relativistic box pressure"]
    description: 用高速粒子碰壁动量转移分析盒壁受力。

  - internal_id: particle_state_from_force_fit
    display_zh: 力位移拟合法
    category: heuristic
    aliases: ["线性拟合测参", "force-position fit"]
    description: 通过外力与位置关系拟合粒子静质量和初速度。

  - internal_id: covariant_energy_conservation
    display_zh: 协变能量守恒
    category: heuristic
    aliases: ["四动量守恒法", "covariant conservation"]
    description: 用四动量守恒避免在特定参考系中硬算分量。

  - internal_id: electromagnetic_stress_energy
    display_zh: 电磁能动张量
    category: physics_law
    aliases: ["应力能量张量", "stress-energy tensor"]
    description: 用张量形式统一描述电磁场能量动量输运。

  - internal_id: charge_density_contraction
    display_zh: 电荷密度收缩
    category: physics_law
    aliases: ["密度洛伦兹变换", "charge density transform"]
    description: 因长度收缩导致不同参考系电荷密度不同。

  - internal_id: current_wire_frame_choice
    display_zh: 载流线换系
    category: heuristic
    aliases: ["导线参考系", "wire frame"]
    description: 选择电子或离子静止系分析载流导线电磁场。

  - internal_id: field_invariant_analysis
    display_zh: 场不变量分析
    category: heuristic
    aliases: ["E²-c²B²", "field invariants"]
    description: 用电磁场不变量判断可否变到纯电场或纯磁场系。

  - internal_id: crossed_fields_drift
    display_zh: 交叉场漂移
    category: physics_model
    aliases: ["E×B漂移", "crossed-field drift"]
    description: 带电粒子在互相垂直电磁场中的整体漂移运动。

  - internal_id: massless_particle_limit
    display_zh: 零质量极限
    category: approximation
    aliases: ["m=0近似", "massless limit"]
    description: 将中微子或光子视为零质量粒子简化运动学。

  - internal_id: small_recoil_approximation
    display_zh: 小反冲近似
    category: approximation
    aliases: ["反冲修正", "small recoil"]
    description: 发射光子后母体速度很小时展开反冲能量修正。

  - internal_id: gamma_recoil_correction
    display_zh: γ反冲修正
    category: physics_law
    aliases: ["核γ反冲", "gamma recoil"]
    description: 原子核发射γ光子时能量需扣除反冲动能。

  - internal_id: decay_chain_rate_equations
    display_zh: 衰变链方程
    category: math_technique
    aliases: ["级联衰变", "decay chain"]
    description: 用耦合微分方程描述母核和子核数量演化。

  - internal_id: excited_state_population_peak
    display_zh: 激发态峰值
    category: math_technique
    aliases: ["粒子数最大时刻", "population peak"]
    description: 对激发态数量函数求极值得到峰值时刻。

  - internal_id: branching_decay_model
    display_zh: 分支衰变模型
    category: physics_model
    aliases: ["多通道衰变", "branching decay model"]
    description: 同一母态按不同衰变常数进入多个末态。

  - internal_id: beta_stability_line
    display_zh: β稳定线
    category: physics_model
    aliases: ["稳定核曲线", "beta stability"]
    description: 由结合能对质子数极值确定稳定核的Z-A关系。

  - internal_id: nuclear_symmetry_energy
    display_zh: 核对称能
    category: physics_law
    aliases: ["不对称能", "symmetry energy"]
    description: 描述质子数和中子数偏离相等时的结合能代价。

  - internal_id: nuclear_coulomb_energy
    display_zh: 核库仑能
    category: physics_law
    aliases: ["质子排斥能", "Coulomb term"]
    description: 原子核内质子间静电排斥降低总结合能。

  - internal_id: nuclear_surface_energy
    display_zh: 核表面能
    category: physics_law
    aliases: ["表面积项", "surface term"]
    description: 表面核子配位数较少导致结合能减少。

  - internal_id: nuclear_volume_energy
    display_zh: 核体积能
    category: physics_law
    aliases: ["体积项", "volume term"]
    description: 核力短程饱和使结合能主项近似正比于核子数。

  - internal_id: nuclear_pairing_energy
    display_zh: 核对能
    category: physics_law
    aliases: ["成对项", "pairing term"]
    description: 质子或中子成对配对使偶偶核额外稳定。

  - internal_id: mirror_nuclei_radius
    display_zh: 镜核半径法
    category: heuristic
    aliases: ["镜核质量差", "mirror nuclei"]
    description: 用镜核库仑能差反推原子核半径参数。

  - internal_id: nuclear_separation_energy
    display_zh: 核子分离能
    category: physics_law
    aliases: ["质子分离能", "neutron separation"]
    description: 从结合能差计算移出一个质子或中子的能量。

  - internal_id: fission_energy_balance
    display_zh: 裂变能量分解
    category: heuristic
    aliases: ["裂变释放能", "fission Q-value"]
    description: 分别比较体积、表面、库仑等项对裂变能的贡献。

  - internal_id: chain_reaction_criticality
    display_zh: 链式反应临界
    category: physics_model
    aliases: ["核裂变链反应", "criticality"]
    description: 中子增殖数达到临界时裂变反应可自持进行。

  - internal_id: neutron_moderation
    display_zh: 中子慢化
    category: physics_model
    aliases: ["快中子减速", "neutron moderation"]
    description: 通过与轻核弹性碰撞降低中子动能。

  - internal_id: elastic_scattering_energy_loss
    display_zh: 弹散能损
    category: physics_law
    aliases: ["碰撞损能", "elastic energy loss"]
    description: 由两体弹性碰撞运动学求入射粒子能量损失。

  - internal_id: fermi_sphere_filling
    display_zh: 费米球填充
    category: heuristic
    aliases: ["动量空间填充", "Fermi sphere"]
    description: 零温费米子按动量空间态从低到高填满。

  - internal_id: pauli_exclusion_counting
    display_zh: 泡利态计数
    category: physics_law
    aliases: ["泡利不相容", "Pauli counting"]
    description: 每个单粒子态按自旋简并度限制占有数。

  - internal_id: infinite_box_energy_levels
    display_zh: 方盒能级
    category: physics_model
    aliases: ["立方势阱", "particle in a box"]
    description: 用三维无限深方势阱估算核子单粒子能级。

  - internal_id: nuclear_fermi_energy
    display_zh: 核费米能
    category: physics_law
    aliases: ["最大占有能", "nuclear Fermi energy"]
    description: 由核子数密度确定质子或中子的最高占有能量。

  - internal_id: degenerate_fermi_pressure
    display_zh: 简并费米压
    category: physics_model
    aliases: ["费米压力", "degeneracy pressure"]
    description: 泡利不相容导致费米气体即使零温也有动能压力。

  - internal_id: nuclear_radius_scaling
    display_zh: 核半径标度
    category: physics_law
    aliases: ["R=r0A^(1/3)", "nuclear radius law"]
    description: 原子核半径随质量数三分之一次方增长。

  - internal_id: spin_spin_coupling
    display_zh: 自旋自旋耦合
    category: physics_law
    aliases: ["自旋点积", "spin-spin coupling"]
    description: 两个自旋角动量点积导致平行反平行能量差。

  - internal_id: magnetic_dipole_contact_field
    display_zh: 磁偶极接触场
    category: physics_law
    aliases: ["δ函数磁场", "contact field"]
    description: 点磁偶极子的奇异接触项影响s态超精细分裂。

  - internal_id: polarized_sphere_regularization
    display_zh: 极化球正则化
    category: math_technique
    aliases: ["均匀极化球", "sphere regularization"]
    description: 用有限极化球处理点偶极场在原点的奇异性。

  - internal_id: g_factor_magnetic_moment
    display_zh: g因子磁矩
    category: physics_law
    aliases: ["朗德g因子", "g-factor"]
    description: 用g因子联系自旋角动量和磁偶极矩大小。

  - internal_id: hyperfine_transition_wavelength
    display_zh: 超精细跃迁波长
    category: physics_model
    aliases: ["21厘米线", "hyperfine wavelength"]
    description: 由超精细能级差求氢原子跃迁辐射波长。
version: "v0.1"
tags:
  - internal_id: effective_potential
    display_zh: 有效势
    category: heuristic
    aliases: ["等效势能", "effective potential"]
    description: 将约束或中心力问题化为一维势能分析。

  - internal_id: phase_portrait_analysis
    display_zh: 相图分析
    category: heuristic
    aliases: ["相平面", "phase portrait"]
    description: 用相空间轨迹判断运动类型和稳定性。

  - internal_id: separatrix_trajectory
    display_zh: 分界轨道
    category: physics_model
    aliases: ["分离曲线", "separatrix"]
    description: 区分周期运动、逃逸运动等不同相空间区域。

  - internal_id: small_oscillation_linearization
    display_zh: 小振动线性化
    category: approximation
    aliases: ["平衡点线性化", "small oscillation"]
    description: 在稳定平衡点附近展开势能得到简谐近似。

  - internal_id: normal_mode_decomposition
    display_zh: 简正模分解
    category: math_technique
    aliases: ["正则模", "normal modes"]
    description: 将耦合振动分解为相互独立的本征振动模式。

  - internal_id: eigenfrequency_equation
    display_zh: 本征频率方程
    category: math_technique
    aliases: ["频率行列式", "characteristic equation"]
    description: 由线性方程组非零解条件求系统本征频率。

  - internal_id: coupled_oscillator_model
    display_zh: 耦合振子模型
    category: physics_model
    aliases: ["多振子耦合", "coupled oscillators"]
    description: 用多个相互作用振子描述能量交换和简正模。

  - internal_id: beat_phenomenon
    display_zh: 拍频现象
    category: physics_model
    aliases: ["能量拍", "beats"]
    description: 近频率模态叠加导致振幅周期性调制。

  - internal_id: driven_resonance
    display_zh: 受迫共振
    category: physics_model
    aliases: ["强迫振动", "driven resonance"]
    description: 外力频率接近固有频率时振幅显著增大。

  - internal_id: damping_quality_factor
    display_zh: 阻尼品质因数
    category: physics_law
    aliases: ["Q因子", "quality factor"]
    description: 用能量损失率刻画弱阻尼振动的锐度。

  - internal_id: slowly_varying_amplitude
    display_zh: 缓变振幅
    category: approximation
    aliases: ["慢变包络", "slow amplitude"]
    description: 在弱阻尼或弱驱动下认为振幅缓慢变化。

  - internal_id: adiabatic_invariant
    display_zh: 绝热不变量
    category: physics_law
    aliases: ["作用量不变量", "adiabatic invariant"]
    description: 缓慢改变参数时作用量积分近似保持不变。

  - internal_id: action_angle_variable
    display_zh: 作用角变量
    category: math_technique
    aliases: ["action-angle", "Jθ变量"]
    description: 用作用量和角变量描述周期系统的演化。

  - internal_id: lagrangian_multiplier_constraint
    display_zh: 约束乘子法
    category: math_technique
    aliases: ["拉格朗日乘子", "constraint multiplier"]
    description: 用乘子力处理几何约束和约束反力。

  - internal_id: generalized_coordinates
    display_zh: 广义坐标
    category: heuristic
    aliases: ["自由度坐标", "generalized coordinates"]
    description: 选取最少独立变量描述受约束系统运动。

  - internal_id: cyclic_coordinate
    display_zh: 循环坐标
    category: heuristic
    aliases: ["可略坐标", "cyclic coordinate"]
    description: 利用拉氏量不显含坐标得到守恒广义动量。

  - internal_id: virtual_work_principle
    display_zh: 虚功原理
    category: physics_law
    aliases: ["虚位移法", "virtual work"]
    description: 用虚位移中约束力不做功化简平衡问题。

  - internal_id: d_alembert_principle
    display_zh: 达朗贝尔原理
    category: physics_law
    aliases: ["惯性力法", "D'Alembert principle"]
    description: 将动力学问题转化为含惯性力的瞬时平衡。

  - internal_id: non_inertial_pseudo_force
    display_zh: 非惯性力
    category: heuristic
    aliases: ["惯性力", "pseudo force"]
    description: 在加速参考系中引入等效力简化相对运动。

  - internal_id: rotating_frame_forces
    display_zh: 转动系惯性力
    category: physics_law
    aliases: ["科氏力离心力", "rotating frame forces"]
    description: 在转动参考系中同时考虑离心力、科氏力和欧拉力。

  - internal_id: coriolis_deflection
    display_zh: 科氏偏转
    category: physics_model
    aliases: ["科里奥利偏转", "Coriolis deflection"]
    description: 转动系中运动物体速度方向因科氏力发生偏转。

  - internal_id: centrifugal_potential
    display_zh: 离心势
    category: physics_law
    aliases: ["离心势能", "centrifugal potential"]
    description: 将离心力写成有效势能并分析平衡位置。

  - internal_id: euler_force
    display_zh: 欧拉力
    category: physics_law
    aliases: ["角加速度惯性力", "Euler force"]
    description: 转动系角速度变化时产生与角加速度相关的惯性力。

  - internal_id: relative_motion_frame
    display_zh: 相对运动系
    category: heuristic
    aliases: ["随体系", "relative frame"]
    description: 选取与某物体共动的参考系简化接触和约束关系。

  - internal_id: instantaneous_center
    display_zh: 瞬心法
    category: heuristic
    aliases: ["瞬时转动中心", "instantaneous center"]
    description: 用瞬时静止点把平面刚体运动视作瞬时转动。

  - internal_id: rolling_without_slipping
    display_zh: 纯滚动约束
    category: physics_law
    aliases: ["无滑滚动", "rolling constraint"]
    description: 接触点瞬时静止并建立平动转动速度关系。

  - internal_id: rolling_with_slipping
    display_zh: 滑滚过渡
    category: physics_model
    aliases: ["有滑滚动", "rolling with slipping"]
    description: 同时处理滑动摩擦和角速度演化直到纯滚动。

  - internal_id: variable_contact_condition
    display_zh: 接触条件判定
    category: heuristic
    aliases: ["脱离条件", "contact condition"]
    description: 通过法向力是否为零判断物体是否脱离约束面。

  - internal_id: normal_force_zero_condition
    display_zh: 零支持力条件
    category: physics_law
    aliases: ["脱离判据", "N=0"]
    description: 支持力降为零时物体刚好离开轨道或接触面。

  - internal_id: friction_direction_self_consistency
    display_zh: 摩擦方向自洽
    category: heuristic
    aliases: ["摩擦反设检验", "friction consistency"]
    description: 先假设摩擦方向再用结果检验相对滑动趋势。

  - internal_id: static_friction_limit
    display_zh: 静摩擦极限
    category: physics_law
    aliases: ["最大静摩擦", "static friction limit"]
    description: 用静摩擦最大值判断约束能否维持不滑动。

  - internal_id: impulsive_friction
    display_zh: 冲量摩擦
    category: physics_model
    aliases: ["摩擦冲量", "friction impulse"]
    description: 碰撞短时过程中用切向冲量改变转动和平动。

  - internal_id: coefficient_of_restitution
    display_zh: 恢复系数
    category: physics_law
    aliases: ["碰撞恢复系数", "restitution coefficient"]
    description: 用碰前碰后法向相对速度比描述碰撞弹性。

  - internal_id: oblique_collision
    display_zh: 斜碰撞
    category: physics_model
    aliases: ["二维碰撞", "oblique impact"]
    description: 分解法向和切向速度处理非正碰过程。

  - internal_id: rigid_body_collision
    display_zh: 刚体碰撞
    category: physics_model
    aliases: ["转动碰撞", "rigid body impact"]
    description: 用冲量矩和角动量变化处理刚体短时碰撞。

  - internal_id: collision_impulse_moment
    display_zh: 碰撞冲量矩
    category: physics_law
    aliases: ["冲量矩定理", "angular impulse"]
    description: 短时碰撞中冲量对质心或接触点产生角动量变化。

  - internal_id: center_of_percussion
    display_zh: 打击中心
    category: physics_model
    aliases: ["撞击中心", "center of percussion"]
    description: 使支点无冲击反力的刚体撞击位置。

  - internal_id: angular_momentum_about_contact
    display_zh: 接触点角动量
    category: heuristic
    aliases: ["绕接触点取矩", "contact angular momentum"]
    description: 选取接触点为参考点以消去未知冲量或约束力矩。

  - internal_id: inertia_tensor_principal_axes
    display_zh: 主轴转动惯量
    category: physics_law
    aliases: ["惯量张量", "principal axes"]
    description: 用主轴系对角化惯量张量简化刚体转动。

  - internal_id: parallel_axis_theorem
    display_zh: 平行轴定理
    category: physics_law
    aliases: ["转动惯量平移", "Steiner theorem"]
    description: 将质心轴转动惯量转换为平行非质心轴惯量。

  - internal_id: perpendicular_axis_theorem
    display_zh: 垂直轴定理
    category: physics_law
    aliases: ["薄板垂轴定理", "perpendicular axis"]
    description: 薄平板绕垂直轴惯量等于面内两轴惯量之和。

  - internal_id: euler_equations_rigid_body
    display_zh: 欧拉动力学方程
    category: physics_law
    aliases: ["刚体欧拉方程", "Euler equations"]
    description: 在刚体主轴系中描述角速度和外力矩演化。

  - internal_id: torque_free_precession
    display_zh: 无力矩进动
    category: physics_model
    aliases: ["自由刚体进动", "torque-free precession"]
    description: 刚体在无外力矩下角速度绕角动量方向进动。

  - internal_id: gyroscopic_precession
    display_zh: 陀螺进动
    category: physics_model
    aliases: ["重力进动", "gyroscopic precession"]
    description: 高速自转刚体在外力矩作用下产生缓慢进动。

  - internal_id: fast_top_approximation
    display_zh: 快陀螺近似
    category: approximation
    aliases: ["高速自转近似", "fast top"]
    description: 自转角速度远大于进动角速度时忽略小量修正。

  - internal_id: nutation_motion
    display_zh: 章动
    category: physics_model
    aliases: ["陀螺章动", "nutation"]
    description: 陀螺轴倾角在进动过程中发生周期性摆动。

  - internal_id: stability_by_energy_extremum
    display_zh: 能量极值稳定
    category: heuristic
    aliases: ["势能二阶判别", "energy stability"]
    description: 通过能量在约束条件下的极值性质判断稳定性。

  - internal_id: lagrange_top_model
    display_zh: 拉格朗日陀螺
    category: physics_model
    aliases: ["对称陀螺", "Lagrange top"]
    description: 一点固定的轴对称刚体在重力场中的运动模型。

  - internal_id: central_force_orbit
    display_zh: 中心力轨道
    category: physics_model
    aliases: ["有心力轨道", "central force orbit"]
    description: 用角动量守恒将中心力运动化为径向轨道方程。

  - internal_id: binet_equation
    display_zh: 比奈方程
    category: math_technique
    aliases: ["Binet equation", "u=1/r方程"]
    description: 用倒半径变量把中心力轨道写成角变量微分方程。

  - internal_id: kepler_orbit_elements
    display_zh: 开普勒轨道要素
    category: physics_model
    aliases: ["椭圆轨道参数", "orbital elements"]
    description: 用半长轴、偏心率等参数描述二体椭圆轨道。

  - internal_id: areal_velocity
    display_zh: 面积速度
    category: physics_law
    aliases: ["开普勒第二定律", "areal velocity"]
    description: 中心力运动中半径矢量扫过面积速率保持常量。

  - internal_id: vis_viva_equation
    display_zh: 活力方程
    category: physics_law
    aliases: ["轨道能量方程", "vis-viva"]
    description: 联系轨道速度、轨道半长轴和当前半径。

  - internal_id: orbit_transfer_energy
    display_zh: 轨道转移能量
    category: heuristic
    aliases: ["变轨能量", "orbit transfer"]
    description: 比较不同轨道能量以求变轨速度增量或燃料需求。

  - internal_id: hohmann_transfer
    display_zh: 霍曼转移
    category: physics_model
    aliases: ["双脉冲转移", "Hohmann transfer"]
    description: 用两次切向脉冲在共面圆轨道间转移。

  - internal_id: gravitational_slingshot
    display_zh: 引力弹弓
    category: physics_model
    aliases: ["重力助推", "gravity assist"]
    description: 在行星参考系中散射再换回太阳系获得速度变化。

  - internal_id: restricted_three_body
    display_zh: 限制性三体
    category: physics_model
    aliases: ["小质量三体", "restricted three-body"]
    description: 两大天体控制下小质量物体的引力运动模型。

  - internal_id: lagrange_points
    display_zh: 拉格朗日点
    category: physics_model
    aliases: ["L点", "Lagrange points"]
    description: 旋转系中引力与离心力平衡形成的特殊位置。

  - internal_id: roche_limit
    display_zh: 洛希极限
    category: physics_model
    aliases: ["潮汐瓦解半径", "Roche limit"]
    description: 天体潮汐力超过自身引力时发生瓦解的临界距离。

  - internal_id: tidal_force_gradient
    display_zh: 潮汐力梯度
    category: physics_law
    aliases: ["引力梯度", "tidal force"]
    description: 由引力场空间变化导致延展物体两端受力不同。

  - internal_id: virial_theorem
    display_zh: 维里定理
    category: physics_law
    aliases: ["均衡定理", "virial theorem"]
    description: 束缚系统长时间平均动能与势能满足特定关系。

  - internal_id: inverse_square_orbit_precession
    display_zh: 轨道进动
    category: physics_model
    aliases: ["近日点进动", "orbital precession"]
    description: 非严格平方反比势导致闭合轨道发生进动。

  - internal_id: perturbative_orbit_precession
    display_zh: 轨道微扰进动
    category: approximation
    aliases: ["小修正进动", "perturbative precession"]
    description: 在开普勒轨道上加入小扰动求近日点进动角。

  - internal_id: variable_mass_rocket
    display_zh: 变质量火箭
    category: physics_model
    aliases: ["火箭方程", "variable mass rocket"]
    description: 用喷出质量相对速度建立火箭速度变化关系。

  - internal_id: tsiolkovsky_equation
    display_zh: 齐奥尔科夫斯基方程
    category: physics_law
    aliases: ["理想火箭方程", "Tsiolkovsky equation"]
    description: 理想火箭速度增量与喷气速度和质量比有关。

  - internal_id: moving_mass_system
    display_zh: 变质量系统选取
    category: heuristic
    aliases: ["开系统动量", "variable mass system"]
    description: 明确系统边界以正确处理质量流入流出动量。

  - internal_id: bead_on_rotating_wire
    display_zh: 转杆小珠模型
    category: physics_model
    aliases: ["旋转杆约束", "bead on rotating rod"]
    description: 小珠受旋转杆约束产生径向运动和约束力变化。

  - internal_id: bead_on_wire_constraint
    display_zh: 线约束小珠
    category: physics_model
    aliases: ["光滑轨道小珠", "bead on wire"]
    description: 小珠沿给定曲线无摩擦运动并受法向约束。

  - internal_id: cycloid_brachistochrone
    display_zh: 最速降线
    category: physics_model
    aliases: ["摆线最速降", "brachistochrone"]
    description: 重力场中连接两点用时最短的光滑轨道问题。

  - internal_id: tautochrone_property
    display_zh: 等时摆线
    category: physics_model
    aliases: ["摆线等时性", "tautochrone"]
    description: 摆线轨道上无摩擦下滑时间与初始位置无关。

  - internal_id: calculus_of_variations
    display_zh: 变分法
    category: math_technique
    aliases: ["欧拉拉格朗日方程", "calculus of variations"]
    description: 通过泛函取极值求最优轨道或最小作用量路径。

  - internal_id: least_action_principle
    display_zh: 最小作用量
    category: physics_law
    aliases: ["哈密顿原理", "least action"]
    description: 真实运动轨迹使作用量在一阶变分下取驻值。

  - internal_id: envelope_method
    display_zh: 包络线法
    category: math_technique
    aliases: ["参数曲线包络", "envelope"]
    description: 消去参数求一族曲线的切触边界。

  - internal_id: caustic_curve
    display_zh: 焦散曲线
    category: physics_model
    aliases: ["包络焦线", "caustic"]
    description: 多条轨迹或射线的包络形成高密度边界曲线。

  - internal_id: dimensional_analysis
    display_zh: 量纲分析
    category: heuristic
    aliases: ["标度估算", "dimensional analysis"]
    description: 用量纲关系推断物理量依赖和数量级。

  - internal_id: scaling_law_method
    display_zh: 标度律方法
    category: heuristic
    aliases: ["尺度分析", "scaling law"]
    description: 通过变量缩放判断主导项和物理量幂律关系。

  - internal_id: limiting_case_check
    display_zh: 极限情形校验
    category: heuristic
    aliases: ["边界检验", "limiting case"]
    description: 用参数趋于零或无穷的结果检验公式合理性。

  - internal_id: asymptotic_matching
    display_zh: 渐近匹配
    category: approximation
    aliases: ["内外解匹配", "asymptotic matching"]
    description: 将不同区域近似解在重叠区匹配成整体解。

  - internal_id: small_parameter_expansion
    display_zh: 小参数展开
    category: approximation
    aliases: ["摄动展开", "small parameter expansion"]
    description: 围绕无量纲小量按阶次保留主导修正。

  - internal_id: dominant_balance
    display_zh: 主导平衡
    category: heuristic
    aliases: ["量级平衡", "dominant balance"]
    description: 比较方程各项量级找出控制过程的主要平衡。

  - internal_id: singular_perturbation
    display_zh: 奇异摄动
    category: approximation
    aliases: ["边界层摄动", "singular perturbation"]
    description: 小参数乘最高阶导数导致解结构发生层状变化。

  - internal_id: energy_landscape_method
    display_zh: 能量地形法
    category: heuristic
    aliases: ["势能曲线法", "energy landscape"]
    description: 通过势能曲线形状判断运动范围和平衡稳定性。

  - internal_id: impulse_approximation
    display_zh: 冲量近似
    category: approximation
    aliases: ["短时作用近似", "impulse approximation"]
    description: 作用时间很短时忽略位移并只累计动量变化。

  - internal_id: sudden_constraint_release
    display_zh: 突然释放约束
    category: physics_model
    aliases: ["约束突变", "sudden release"]
    description: 约束瞬间消失后速度连续而受力条件突变。

  - internal_id: quasi_static_process
    display_zh: 准静态过程
    category: approximation
    aliases: ["缓慢变化", "quasi-static"]
    description: 外参变化足够慢时系统近似连续处于平衡状态。

  - internal_id: terminal_velocity_balance
    display_zh: 终端速度平衡
    category: physics_model
    aliases: ["阻力平衡速度", "terminal velocity"]
    description: 阻力与驱动力平衡后物体达到稳定速度。

  - internal_id: quadratic_drag_model
    display_zh: 平方阻力模型
    category: physics_model
    aliases: ["高速阻力", "quadratic drag"]
    description: 阻力大小与速度平方近似成正比的流体阻力模型。

  - internal_id: linear_drag_model
    display_zh: 线性阻力模型
    category: physics_model
    aliases: ["斯托克斯阻力", "linear drag"]
    description: 低雷诺数下阻力与速度近似成正比。

  - internal_id: variable_acceleration_integration
    display_zh: 变加速积分
    category: math_technique
    aliases: ["分离变量运动", "variable acceleration"]
    description: 通过变量代换或分离变量积分求非恒定加速度运动。

  - internal_id: nonuniform_string_tension
    display_zh: 非均匀绳张力
    category: physics_model
    aliases: ["变张力绳", "nonuniform tension"]
    description: 有质量绳或加速绳中张力随位置改变。

  - internal_id: massive_pulley_system
    display_zh: 有质量滑轮
    category: physics_model
    aliases: ["转动滑轮", "massive pulley"]
    description: 滑轮转动惯量导致两侧绳张力不再相等。

  - internal_id: moving_pulley_constraint
    display_zh: 动滑轮约束
    category: heuristic
    aliases: ["绳长约束", "pulley constraint"]
    description: 通过绳长不变建立多个物体位移和加速度关系。

  - internal_id: variable_length_pendulum
    display_zh: 变长摆
    category: physics_model
    aliases: ["收绳摆", "variable pendulum"]
    description: 摆长随时间变化时角动量或能量发生演化。

  - internal_id: spherical_pendulum
    display_zh: 球摆
    category: physics_model
    aliases: ["三维单摆", "spherical pendulum"]
    description: 质点在固定长度约束下于空间曲面上运动。

  - internal_id: conical_pendulum
    display_zh: 圆锥摆
    category: physics_model
    aliases: ["锥摆", "conical pendulum"]
    description: 摆球以恒定倾角绕竖直轴作圆周运动。

  - internal_id: parametric_resonance
    display_zh: 参数共振
    category: physics_model
    aliases: ["参量激发", "parametric resonance"]
    description: 系统参数周期变化导致振幅指数增长。

  - internal_id: mathieu_equation
    display_zh: 马 Mathieu 方程
    category: math_technique
    aliases: ["Mathieu equation", "参数振动方程"]
    description: 描述参数周期变化振子的线性微分方程。

  - internal_id: pendulum_large_angle_integral
    display_zh: 大角摆积分
    category: math_technique
    aliases: ["椭圆积分摆", "large-angle pendulum"]
    description: 不作小角近似时用能量积分求摆的周期。

  - internal_id: elliptic_integral_period
    display_zh: 椭圆积分周期
    category: math_technique
    aliases: ["第一类椭圆积分", "elliptic integral"]
    description: 大振幅非线性周期运动常化为椭圆积分形式。

  - internal_id: nonlinear_frequency_shift
    display_zh: 非线性频移
    category: approximation
    aliases: ["振幅依赖频率", "nonlinear frequency shift"]
    description: 非线性项使振动频率依赖于振幅大小。

  - internal_id: continuum_limit_chain
    display_zh: 链模型连续极限
    category: approximation
    aliases: ["离散到连续", "continuum limit"]
    description: 将大量离散质点链在长波极限化为连续介质。

  - internal_id: wave_on_string
    display_zh: 弦波方程
    category: physics_model
    aliases: ["横波弦模型", "string wave"]
    description: 用张力和线密度推导弦上横波传播速度。

  - internal_id: normal_modes_string
    display_zh: 弦简正模
    category: physics_model
    aliases: ["驻波模态", "string normal modes"]
    description: 由边界条件确定弦的驻波频率和模态形状。

  - internal_id: dispersion_relation
    display_zh: 色散关系
    category: physics_law
    aliases: ["ω-k关系", "dispersion relation"]
    description: 描述波的频率与波数之间的函数关系。

  - internal_id: group_velocity
    display_zh: 群速度
    category: physics_law
    aliases: ["波包速度", "group velocity"]
    description: 波包包络传播速度等于频率对波数的导数。

  - internal_id: phase_velocity
    display_zh: 相速度
    category: physics_law
    aliases: ["相位速度", "phase velocity"]
    description: 单一相位面传播速度等于频率除以波数。

  - internal_id: shock_wave_kinematics
    display_zh: 激波运动学
    category: physics_model
    aliases: ["冲击波", "shock wave"]
    description: 扰动速度超过介质传播速度时形成陡峭波前。

  - internal_id: mach_cone
    display_zh: 马赫锥
    category: physics_model
    aliases: ["超声速锥", "Mach cone"]
    description: 超声速运动源产生锥形波前并满足马赫角关系。

  - internal_id: fluid_bernoulli_streamline
    display_zh: 伯努利流线
    category: physics_law
    aliases: ["伯努利方程", "Bernoulli equation"]
    description: 理想定常流中沿流线压强、动能和势能总和守恒。

  - internal_id: continuity_equation_flow
    display_zh: 连续性方程
    category: physics_law
    aliases: ["流量守恒", "continuity equation"]
    description: 不可压或稳态流动中质量流率保持连续。

  - internal_id: torricelli_law
    display_zh: 托里拆利定律
    category: physics_law
    aliases: ["孔流速度", "Torricelli law"]
    description: 液体从小孔流出速度由液面高度差决定。

  - internal_id: added_mass_effect
    display_zh: 附加质量效应
    category: physics_model
    aliases: ["流体附加惯量", "added mass"]
    description: 物体在流体中加速时需同时带动周围流体运动。

  - internal_id: surface_tension_pressure
    display_zh: 表面张力压差
    category: physics_law
    aliases: ["拉普拉斯压强", "Laplace pressure"]
    description: 曲面液膜两侧压强差由表面张力和曲率决定。

  - internal_id: capillary_rise
    display_zh: 毛细上升
    category: physics_model
    aliases: ["毛细现象", "capillary rise"]
    description: 表面张力和重力平衡决定细管中液面高度。

  - internal_id: dimensional_boundary_layer
    display_zh: 边界层估算
    category: heuristic
    aliases: ["边界层尺度", "boundary layer"]
    description: 用量纲和主导平衡估算粘性影响区域厚度。

  - internal_id: reynolds_number_scaling
    display_zh: 雷诺数标度
    category: heuristic
    aliases: ["惯性粘性比", "Reynolds number"]
    description: 用雷诺数判断流动中惯性力和粘性力相对强弱。

  - internal_id: poisson_bracket_conservation
    display_zh: 泊松括号守恒
    category: math_technique
    aliases: ["Poisson bracket", "正则守恒"]
    description: 用泊松括号判断物理量是否为运动积分。

  - internal_id: hamiltonian_phase_flow
    display_zh: 哈密顿相流
    category: physics_law
    aliases: ["相空间流", "Hamiltonian flow"]
    description: 哈密顿方程给出相空间中正则变量的演化。

  - internal_id: liouville_theorem
    display_zh: 刘维尔定理
    category: physics_law
    aliases: ["相体积守恒", "Liouville theorem"]
    description: 哈密顿系统在相空间中的体积随时间保持不变。

  - internal_id: canonical_transformation
    display_zh: 正则变换
    category: math_technique
    aliases: ["canonical transform", "辛变换"]
    description: 保持哈密顿方程形式不变的相空间变量变换。

  - internal_id: hamilton_jacobi_method
    display_zh: 哈密顿雅可比法
    category: math_technique
    aliases: ["HJ方程", "Hamilton-Jacobi"]
    description: 通过主函数求解可分离哈密顿系统的运动。

  - internal_id: separable_coordinates
    display_zh: 可分离坐标
    category: heuristic
    aliases: ["变量分离坐标", "separable coordinates"]
    description: 选择合适坐标系使动力学方程分离求解。

  - internal_id: noether_symmetry
    display_zh: 诺特对称性
    category: physics_law
    aliases: ["对称守恒", "Noether symmetry"]
    description: 连续对称性对应能量、动量或角动量守恒量。

  - internal_id: constraint_force_elimination
    display_zh: 约束力消去
    category: heuristic
    aliases: ["避开约束反力", "constraint elimination"]
    description: 通过取矩、能量或虚功方法消去未知约束力。

  - internal_id: smart_origin_torque
    display_zh: 巧选力矩点
    category: heuristic
    aliases: ["取矩点选择", "torque origin"]
    description: 选取力作用线交点或瞬心使未知力矩为零。

  - internal_id: momentum_flux_force
    display_zh: 动量流力
    category: physics_law
    aliases: ["动量通量", "momentum flux"]
    description: 通过单位时间流入流出动量差求连续介质受力。

  - internal_id: center_of_mass_separation
    display_zh: 质心相对分离
    category: heuristic
    aliases: ["质心系分解", "CM-relative split"]
    description: 将二体问题分解为质心运动和相对运动。

  - internal_id: reduced_mass_method
    display_zh: 约化质量法
    category: math_technique
    aliases: ["折合质量", "reduced mass"]
    description: 用约化质量把二体相对运动化为单体中心力问题。

  - internal_id: elastic_scattering_cm
    display_zh: 质心弹散
    category: physics_model
    aliases: ["质心系弹性散射", "CM elastic scattering"]
    description: 在质心系中用速度反向或转角处理弹性散射。

  - internal_id: hard_sphere_scattering
    display_zh: 硬球散射
    category: physics_model
    aliases: ["刚球碰撞散射", "hard sphere scattering"]
    description: 粒子与刚性球面弹性碰撞形成几何散射截面。

  - internal_id: scattering_cross_section_mechanics
    display_zh: 力学散射截面
    category: physics_law
    aliases: ["经典截面", "mechanical cross section"]
    description: 用瞄准距离到散射角的映射计算散射概率。

  - internal_id: rainbow_scattering
    display_zh: 彩虹散射
    category: physics_model
    aliases: ["彩虹角", "rainbow scattering"]
    description: 散射角对瞄准距离取极值时形成强度增强。

  - internal_id: caustic_in_mechanics
    display_zh: 力学焦散
    category: physics_model
    aliases: ["轨迹焦散", "mechanical caustic"]
    description: 一族粒子轨迹包络导致空间密度显著增大。

  - internal_id: elliptic_orbit_time
    display_zh: 椭圆轨道时间
    category: math_technique
    aliases: ["开普勒方程", "Kepler equation"]
    description: 用偏近点角或开普勒方程计算椭圆轨道时间关系。

  - internal_id: hodograph_method
    display_zh: 速度图法
    category: heuristic
    aliases: ["hodograph", "速度矢量图"]
    description: 在速度空间中研究中心力轨道和散射过程。

  - internal_id: laplace_runge_lenz_vector
    display_zh: 龙格楞次矢量
    category: physics_law
    aliases: ["LRL矢量", "Runge-Lenz vector"]
    description: 平方反比中心力中指向近心点的额外守恒矢量。

  - internal_id: inverse_problem_central_force
    display_zh: 中心力反问题
    category: math_technique
    aliases: ["轨道反推力", "inverse central force"]
    description: 根据给定轨道形状反推出所需中心力形式。

  - internal_id: stable_circular_orbit_condition
    display_zh: 圆轨稳定条件
    category: heuristic
    aliases: ["圆轨二阶判据", "stable circular orbit"]
    description: 通过有效势二阶导数判断圆轨道稳定性。

  - internal_id: epicyclic_frequency
    display_zh: 径向振动频率
    category: physics_model
    aliases: ["epicyclic frequency", "周转频率"]
    description: 圆轨附近小径向扰动产生的振动频率。

  - internal_id: tidal_locking_model
    display_zh: 潮汐锁定模型
    category: physics_model
    aliases: ["同步自转", "tidal locking"]
    description: 潮汐耗散使天体自转周期趋于公转周期。

  - internal_id: energy_dissipation_stability
    display_zh: 耗散趋稳
    category: heuristic
    aliases: ["能量耗散选择", "dissipative stability"]
    description: 有耗散系统在约束下趋向能量较低的稳定状态。

  - internal_id: parametric_constraint_differentiation
    display_zh: 约束微分法
    category: math_technique
    aliases: ["绳长微分", "constraint differentiation"]
    description: 对几何约束连续求导得到速度和加速度关系。

  - internal_id: instantaneous_power_method
    display_zh: 瞬时功率法
    category: heuristic
    aliases: ["功率平衡", "power method"]
    description: 用外力功率与机械能变化率建立运动方程。

  - internal_id: work_by_constraint_motion
    display_zh: 动约束做功
    category: physics_model
    aliases: ["移动约束做功", "moving constraint work"]
    description: 约束边界运动时约束力可能对系统做功。

  - internal_id: moving_wedge_model
    display_zh: 可动斜面模型
    category: physics_model
    aliases: ["滑块斜面系统", "moving wedge"]
    description: 滑块与可动斜面相互约束并共同运动的模型。

  - internal_id: center_of_mass_constraint
    display_zh: 质心约束法
    category: heuristic
    aliases: ["水平质心不动", "CM constraint"]
    description: 外力某方向为零时利用质心运动约束求相对位移。

  - internal_id: many_body_symmetry_reduction
    display_zh: 多体对称约化
    category: heuristic
    aliases: ["对称降维", "symmetry reduction"]
    description: 利用几何或质量对称性减少多体问题自由度。

  - internal_id: continuum_mass_element
    display_zh: 连续体微元
    category: heuristic
    aliases: ["质量微元法", "mass element"]
    description: 取微小质量元建立连续体的积分方程。

  - internal_id: variable_density_inertia
    display_zh: 变密度转动惯量
    category: math_technique
    aliases: ["密度积分惯量", "variable density inertia"]
    description: 对非均匀质量分布积分求转动惯量或质心。

  - internal_id: center_of_mass_integral
    display_zh: 质心积分
    category: math_technique
    aliases: ["形心积分", "CM integral"]
    description: 对连续质量分布积分求质心坐标。

  - internal_id: tensor_inertia_integration
    display_zh: 惯量张量积分
    category: math_technique
    aliases: ["转动惯量张量", "inertia tensor"]
    description: 对质量分布积分得到刚体惯量张量各分量。

  - internal_id: perturbative_equilibrium_shift
    display_zh: 平衡点微扰
    category: approximation
    aliases: ["平衡位置修正", "equilibrium perturbation"]
    description: 在小外参作用下求平衡位置的一阶修正。

  - internal_id: second_variation_stability
    display_zh: 二阶变分稳定
    category: math_technique
    aliases: ["二变分判据", "second variation"]
    description: 用二阶变分正定性判断平衡或轨迹稳定性。

  - internal_id: catastrophe_fold_model
    display_zh: 折叠突变
    category: physics_model
    aliases: ["鞍结分岔", "fold catastrophe"]
    description: 参数变化使稳定与不稳定平衡点合并消失。

  - internal_id: bifurcation_analysis
    display_zh: 分岔分析
    category: heuristic
    aliases: ["稳定性分岔", "bifurcation"]
    description: 分析控制参数变化导致平衡或运动形态突变。

  - internal_id: elliptic_stability_matrix
    display_zh: 稳定矩阵法
    category: math_technique
    aliases: ["线性稳定矩阵", "stability matrix"]
    description: 对运动方程线性化并由特征值判断稳定性。

  - internal_id: constrained_energy_minimization
    display_zh: 约束能量极小
    category: heuristic
    aliases: ["条件极值稳定", "constrained minimum"]
    description: 在约束条件下最小化能量求平衡构型。

  - internal_id: variational_boundary_condition
    display_zh: 变分边界条件
    category: math_technique
    aliases: ["自然边界条件", "natural boundary"]
    description: 变分问题中端点自由时自动产生边界条件。

  - internal_id: catenary_model
    display_zh: 悬链线模型
    category: physics_model
    aliases: ["悬链线", "catenary"]
    description: 均匀柔绳在重力下静态平衡形成双曲余弦曲线。

  - internal_id: elastica_model
    display_zh: 弹性杆模型
    category: physics_model
    aliases: ["欧拉弹性线", "elastica"]
    description: 细杆弯曲能和外力平衡决定其平面形状。

  - internal_id: buckling_instability
    display_zh: 屈曲失稳
    category: physics_model
    aliases: ["欧拉屈曲", "buckling"]
    description: 受压细杆超过临界载荷后直线平衡失稳。

  - internal_id: bending_energy_minimization
    display_zh: 弯曲能极小
    category: heuristic
    aliases: ["弹性势能极小", "bending energy"]
    description: 通过最小化弯曲能求弹性线形状或稳定构型。

  - internal_id: granular_avalanche_angle
    display_zh: 堆积角模型
    category: physics_model
    aliases: ["休止角", "angle of repose"]
    description: 颗粒堆表面由摩擦极限决定最大稳定倾角。

  - internal_id: continuum_rod_force_balance
    display_zh: 杆微元平衡
    category: heuristic
    aliases: ["杆内力平衡", "rod element balance"]
    description: 对细杆微元列力和力矩平衡方程求内力分布。

  - internal_id: string_shape_under_load
    display_zh: 载荷下绳形
    category: physics_model
    aliases: ["受力柔索", "loaded string"]
    description: 柔绳在分布载荷作用下形状由张力平衡决定。

  - internal_id: static_indeterminacy
    display_zh: 静不定问题
    category: heuristic
    aliases: ["超静定", "statically indeterminate"]
    description: 平衡方程不足时需结合形变协调条件求解。

  - internal_id: compatibility_condition
    display_zh: 协调条件
    category: physics_law
    aliases: ["形变协调", "compatibility"]
    description: 多个约束或弹性体形变必须满足几何相容关系。

  - internal_id: elastic_energy_method
    display_zh: 弹性能量法
    category: heuristic
    aliases: ["应变能法", "elastic energy"]
    description: 用弹性势能和功的关系求形变、力或稳定性。

  - internal_id: castigliano_theorem
    display_zh: 卡氏定理
    category: physics_law
    aliases: ["Castigliano theorem", "应变能偏导"]
    description: 弹性结构位移可由应变能对外力求偏导得到。

  - internal_id: principal_stress_analysis
    display_zh: 主应力分析
    category: math_technique
    aliases: ["应力张量主轴", "principal stress"]
    description: 对应力张量对角化求主应力和主方向。

  - internal_id: mohr_circle
    display_zh: 莫尔圆
    category: math_technique
    aliases: ["应力圆", "Mohr circle"]
    description: 用几何圆图表示平面应力变换和极值应力。

  - internal_id: rotational_energy_partition
    display_zh: 转动能分解
    category: heuristic
    aliases: ["平动转动分解", "rotation energy split"]
    description: 将刚体动能分为质心平动能和绕质心转动能。

  - internal_id: instantaneous_axis_rotation
    display_zh: 瞬时转轴
    category: heuristic
    aliases: ["瞬轴法", "instantaneous axis"]
    description: 空间刚体运动可在瞬间视作绕某轴转动和平移。

  - internal_id: no_slip_constraint_graph
    display_zh: 无滑速度图
    category: heuristic
    aliases: ["速度矢量图", "no-slip velocity diagram"]
    description: 用接触点速度相等画图建立滚动系统速度关系。

  - internal_id: compound_pendulum
    display_zh: 复摆
    category: physics_model
    aliases: ["物理摆", "compound pendulum"]
    description: 刚体绕固定水平轴在重力矩作用下摆动。

  - internal_id: equivalent_pendulum_length
    display_zh: 等效摆长
    category: physics_law
    aliases: ["物理摆摆长", "equivalent length"]
    description: 用转动惯量和质心距确定物理摆等效单摆长度。

  - internal_id: moving_support_pendulum
    display_zh: 移动支点摆
    category: physics_model
    aliases: ["加速支点摆", "moving support pendulum"]
    description: 摆的悬点运动导致等效重力和驱动项改变。

  - internal_id: kapitza_pendulum
    display_zh: 卡皮查摆
    category: physics_model
    aliases: ["倒立稳定摆", "Kapitza pendulum"]
    description: 高频振动支点可使倒立位置动态稳定。

  - internal_id: time_average_effective_potential
    display_zh: 时间平均有效势
    category: approximation
    aliases: ["高频平均势", "averaged potential"]
    description: 对快速振动自由度平均得到慢变量有效势。

  - internal_id: multiple_scale_method
    display_zh: 多重尺度法
    category: math_technique
    aliases: ["快慢变量法", "multiple scales"]
    description: 引入多个时间尺度处理缓慢调制的近似解。

  - internal_id: secular_term_removal
    display_zh: 久期项消去
    category: approximation
    aliases: ["消除发散项", "secular removal"]
    description: 通过修正频率或振幅避免摄动解出现随时间增长项。

  - internal_id: resonance_width_estimate
    display_zh: 共振宽度估算
    category: approximation
    aliases: ["半高宽", "resonance width"]
    description: 估算受迫或参数共振中显著响应的频率范围。

  - internal_id: energy_phase_plane
    display_zh: 能量相轨
    category: heuristic
    aliases: ["相轨能量线", "energy phase curve"]
    description: 用能量守恒在相平面中画出运动轨迹。

  - internal_id: turning_point_analysis
    display_zh: 转折点分析
    category: heuristic
    aliases: ["运动端点", "turning point"]
    description: 由动能为零的位置确定运动范围边界。

  - internal_id: escape_velocity_general
    display_zh: 逃逸速度
    category: physics_law
    aliases: ["逃逸条件", "escape velocity"]
    description: 由总机械能非负确定脱离束缚势场的临界速度。

  - internal_id: capture_orbit_condition
    display_zh: 俘获轨道条件
    category: physics_model
    aliases: ["束缚判据", "capture condition"]
    description: 总能量和角动量满足条件时粒子进入束缚轨道。

  - internal_id: scattering_angle_integral
    display_zh: 散射角积分
    category: math_technique
    aliases: ["偏转角积分", "deflection integral"]
    description: 由径向有效势积分求中心势散射偏转角。

  - internal_id: small_angle_scattering
    display_zh: 小角散射近似
    category: approximation
    aliases: ["微小偏折", "small-angle scattering"]
    description: 偏转角很小时沿未扰直线路径积分横向力。

  - internal_id: transverse_impulse_method
    display_zh: 横向冲量法
    category: heuristic
    aliases: ["侧向冲量", "transverse impulse"]
    description: 对近直线运动累积横向力冲量求偏转角。

  - internal_id: finite_time_collision
    display_zh: 有限时碰撞
    category: physics_model
    aliases: ["非瞬时碰撞", "finite collision time"]
    description: 碰撞持续时间不可忽略时需分析接触力演化。

  - internal_id: two_stage_motion_split
    display_zh: 分阶段运动
    category: heuristic
    aliases: ["阶段拆解", "piecewise motion"]
    description: 将约束、接触或受力改变前后分段建立方程。

  - internal_id: event_sequence_tracking
    display_zh: 事件序列追踪
    category: heuristic
    aliases: ["关键时刻排序", "event tracking"]
    description: 按脱离、碰撞、转折等关键事件顺序组织长题计算。

  - internal_id: root_selection_physical
    display_zh: 物理解根选择
    category: heuristic
    aliases: ["舍去伪根", "physical root"]
    description: 由时间正性、速度方向和约束条件筛选数学根。

  - internal_id: nondimensionalization
    display_zh: 无量纲化
    category: math_technique
    aliases: ["量纲归一", "nondimensionalization"]
    description: 引入特征尺度减少参数并暴露控制无量纲数。

  - internal_id: conserved_quantity_hunting
    display_zh: 守恒量寻找
    category: heuristic
    aliases: ["寻找积分常量", "conservation hunting"]
    description: 根据对称性、循环变量或外力矩判断可用守恒量。

  - internal_id: hidden_symmetry
    display_zh: 隐含对称性
    category: heuristic
    aliases: ["隐藏守恒", "hidden symmetry"]
    description: 识别不显然的对称性以发现额外守恒量。

  - internal_id: problem_frame_switching
    display_zh: 换系简化
    category: heuristic
    aliases: ["参考系选择", "frame switching"]
    description: 选择惯性系、质心系或非惯性系降低计算复杂度。
