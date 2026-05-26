version: "v0.1"
tags:
  - internal_id: image_charge_method
    display_zh: 镜像电荷法
    category: heuristic
    aliases: ["电像法", "method of images"]
    description: 用虚设电荷满足导体边界条件求静电场。

  - internal_id: grounded_conductor_boundary
    display_zh: 接地导体边界
    category: physics_model
    aliases: ["零电势边界", "grounded conductor"]
    description: 接地导体表面电势固定为零并重排感应电荷。

  - internal_id: conducting_sphere_image
    display_zh: 导体球电像
    category: physics_model
    aliases: ["球面镜像电荷", "sphere image charge"]
    description: 点电荷与接地导体球问题的经典镜像模型。

  - internal_id: conducting_plane_image
    display_zh: 导体平面电像
    category: physics_model
    aliases: ["平面镜像电荷", "plane image charge"]
    description: 点电荷与无限接地导体平面的镜像求解模型。

  - internal_id: multipole_expansion
    display_zh: 多极展开
    category: math_technique
    aliases: ["多极矩展开", "multipole expansion"]
    description: 远场中按单极、偶极、四极等阶次展开电势。

  - internal_id: electric_dipole_field
    display_zh: 电偶极场
    category: physics_model
    aliases: ["电偶极子", "electric dipole"]
    description: 用电偶极矩描述等量异号近邻电荷的远场。

  - internal_id: magnetic_dipole_field
    display_zh: 磁偶极场
    category: physics_model
    aliases: ["磁偶极子", "magnetic dipole"]
    description: 用磁偶极矩描述小电流环或磁体远场。

  - internal_id: dipole_in_external_field
    display_zh: 偶极外场能
    category: physics_law
    aliases: ["偶极能量", "dipole energy"]
    description: 偶极矩在外场中具有取向相关势能和力矩。

  - internal_id: induced_dipole_polarization
    display_zh: 诱导偶极极化
    category: physics_model
    aliases: ["感生偶极", "induced dipole"]
    description: 外电场使可极化物体产生与场相关的偶极矩。

  - internal_id: polarizability_model
    display_zh: 极化率模型
    category: physics_model
    aliases: ["电极化率", "polarizability"]
    description: 用极化率联系外电场和诱导偶极矩大小。

  - internal_id: dielectric_sphere_in_field
    display_zh: 介质球外场
    category: physics_model
    aliases: ["均匀介质球", "dielectric sphere"]
    description: 均匀介质球置于匀强外电场中的极化模型。

  - internal_id: conducting_sphere_in_field
    display_zh: 导体球外场
    category: physics_model
    aliases: ["导体球极化", "conducting sphere"]
    description: 导体球在匀强外电场中感应出偶极型面电荷。

  - internal_id: laplace_equation_separation
    display_zh: 拉普拉斯方程分离
    category: math_technique
    aliases: ["分离变量法", "Laplace separation"]
    description: 在合适坐标中分离变量求无源区域电势。

  - internal_id: poisson_equation_solution
    display_zh: 泊松方程求势
    category: math_technique
    aliases: ["Poisson equation", "有源电势方程"]
    description: 由电荷密度作为源项求解空间电势分布。

  - internal_id: green_function_electrostatics
    display_zh: 静电格林函数
    category: math_technique
    aliases: ["Green函数", "electrostatic Green function"]
    description: 用点源响应函数构造满足边界的电势解。

  - internal_id: uniqueness_theorem
    display_zh: 唯一性定理
    category: physics_law
    aliases: ["静电唯一性", "uniqueness theorem"]
    description: 给定边界条件时静电势解唯一，从而验证构造解。

  - internal_id: boundary_condition_matching
    display_zh: 边界条件匹配
    category: heuristic
    aliases: ["边界匹配", "boundary matching"]
    description: 在界面处匹配电势、场分量或位移矢量条件。

  - internal_id: surface_charge_from_field_jump
    display_zh: 场跃变求面电荷
    category: physics_law
    aliases: ["法向场跃变", "surface charge"]
    description: 电场法向分量跃变由界面自由面电荷决定。

  - internal_id: tangential_field_continuity
    display_zh: 切向电场连续
    category: physics_law
    aliases: ["Et连续", "tangential E continuity"]
    description: 静电场在界面两侧切向分量保持连续。

  - internal_id: displacement_boundary_condition
    display_zh: 电位移边界
    category: physics_law
    aliases: ["D边界条件", "displacement boundary"]
    description: 电位移法向跃变等于界面自由面电荷密度。

  - internal_id: dielectric_interface_refraction
    display_zh: 电场折射
    category: physics_model
    aliases: ["电力线折射", "field refraction"]
    description: 电场线穿过介质界面时方向按介电常数发生偏折。

  - internal_id: capacitance_matrix
    display_zh: 电容矩阵
    category: physics_model
    aliases: ["多导体电容", "capacitance matrix"]
    description: 用线性矩阵关系描述多导体电荷与电势。

  - internal_id: capacitance_energy_method
    display_zh: 电容能量法
    category: heuristic
    aliases: ["电场能求力", "capacitor energy"]
    description: 用电容随几何参数变化求电场力或稳定性。

  - internal_id: electrostatic_pressure
    display_zh: 静电压强
    category: physics_law
    aliases: ["电场压力", "electrostatic pressure"]
    description: 导体表面电场产生与场强平方成正比的向外压强。

  - internal_id: maxwell_stress_tensor
    display_zh: 麦克斯韦应力张量
    category: physics_law
    aliases: ["电磁应力张量", "Maxwell stress tensor"]
    description: 用场的应力张量计算电磁力和力矩。

  - internal_id: virtual_work_electrostatics
    display_zh: 静电虚功法
    category: heuristic
    aliases: ["电势能求力", "electrostatic virtual work"]
    description: 通过虚位移下电场能变化求广义力。

  - internal_id: constant_voltage_energy
    display_zh: 恒压能量修正
    category: heuristic
    aliases: ["电源做功", "constant voltage energy"]
    description: 电容接电源时求力需计入电源做功的能量差。

  - internal_id: constant_charge_energy
    display_zh: 恒荷能量法
    category: heuristic
    aliases: ["孤立电容能", "constant charge energy"]
    description: 电荷固定时直接由电场能变化求机械力。

  - internal_id: electrostatic_stability
    display_zh: 静电稳定性
    category: heuristic
    aliases: ["电场平衡稳定", "electrostatic stability"]
    description: 通过电势能二阶变化判断带电系统平衡稳定性。

  - internal_id: earnshaw_theorem
    display_zh: 恩绍定理
    category: physics_law
    aliases: ["Earnshaw theorem", "静电无稳定悬浮"]
    description: 纯静电平方反比力场不能形成稳定悬浮平衡。

  - internal_id: conformal_mapping
    display_zh: 保角变换
    category: math_technique
    aliases: ["共形映射", "conformal mapping"]
    description: 用复变函数变换二维边界以求静电场。

  - internal_id: complex_potential_method
    display_zh: 复势法
    category: math_technique
    aliases: ["复电势", "complex potential"]
    description: 用解析函数表示二维静电势和流线结构。

  - internal_id: logarithmic_potential_2d
    display_zh: 二维对数势
    category: physics_model
    aliases: ["线电荷势", "log potential"]
    description: 无限长线电荷在二维截面中产生对数型电势。

  - internal_id: coaxial_capacitor_model
    display_zh: 同轴电容器
    category: physics_model
    aliases: ["圆柱电容", "coaxial capacitor"]
    description: 利用柱对称电场计算同轴导体间电容和能量。

  - internal_id: spherical_capacitor_model
    display_zh: 球形电容器
    category: physics_model
    aliases: ["同心球电容", "spherical capacitor"]
    description: 利用球对称电场计算同心导体球壳电容。

  - internal_id: fringing_field_approximation
    display_zh: 边缘场近似
    category: approximation
    aliases: ["边缘效应", "fringing field"]
    description: 对非理想电容器边缘电场进行近似修正。

  - internal_id: charge_relaxation
    display_zh: 电荷弛豫
    category: physics_model
    aliases: ["弛豫时间", "charge relaxation"]
    description: 导电介质中自由电荷按特征时间衰减重排。

  - internal_id: leaky_dielectric_model
    display_zh: 漏电介质模型
    category: physics_model
    aliases: ["弱导电介质", "leaky dielectric"]
    description: 同时考虑介电极化与有限电导导致的电荷泄漏。

  - internal_id: rc_transient_response
    display_zh: RC暂态响应
    category: physics_model
    aliases: ["电容充放电", "RC transient"]
    description: 电阻电容网络中电压电流按指数规律演化。

  - internal_id: kirchhoff_network_reduction
    display_zh: 基尔霍夫网络约化
    category: heuristic
    aliases: ["电路方程约化", "Kirchhoff reduction"]
    description: 用节点电势和回路电流系统化求解复杂电路。

  - internal_id: node_potential_method
    display_zh: 节点电势法
    category: math_technique
    aliases: ["节点法", "nodal analysis"]
    description: 以节点电势为未知量列电流连续方程求电路。

  - internal_id: mesh_current_method
    display_zh: 网孔电流法
    category: math_technique
    aliases: ["回路电流法", "mesh analysis"]
    description: 以独立网孔电流为未知量列回路电压方程。

  - internal_id: thevenin_equivalent
    display_zh: 戴维南等效
    category: heuristic
    aliases: ["等效电压源", "Thevenin equivalent"]
    description: 将线性双端网络等效为电压源串联电阻。

  - internal_id: norton_equivalent
    display_zh: 诺顿等效
    category: heuristic
    aliases: ["等效电流源", "Norton equivalent"]
    description: 将线性双端网络等效为电流源并联电阻。

  - internal_id: maximum_power_transfer
    display_zh: 最大功率传输
    category: physics_law
    aliases: ["负载匹配", "maximum power"]
    description: 负载与等效内阻匹配时输出功率最大。

  - internal_id: bridge_balance_condition
    display_zh: 电桥平衡
    category: physics_model
    aliases: ["惠斯通电桥", "bridge balance"]
    description: 电桥两中点等电势时桥支路无电流。

  - internal_id: symmetry_circuit_shortcut
    display_zh: 电路对称简化
    category: heuristic
    aliases: ["等势点合并", "circuit symmetry"]
    description: 利用对称性寻找等势点以合并或删除支路。

  - internal_id: infinite_resistor_network
    display_zh: 无限电阻网络
    category: physics_model
    aliases: ["无限网络", "infinite resistor lattice"]
    description: 用自相似或格林函数处理无限电阻阵列等效电阻。

  - internal_id: self_similarity_circuit
    display_zh: 电路自相似
    category: heuristic
    aliases: ["递归等效", "self-similar circuit"]
    description: 利用无限电路局部结构重复建立递推方程。

  - internal_id: distributed_rc_line
    display_zh: 分布RC线
    category: physics_model
    aliases: ["RC传输线", "distributed RC"]
    description: 将连续电阻电容线化为扩散型电压传播方程。

  - internal_id: transmission_line_model
    display_zh: 传输线模型
    category: physics_model
    aliases: ["分布参数线", "transmission line"]
    description: 用分布电感电容描述电磁信号沿导线传播。

  - internal_id: telegrapher_equations
    display_zh: 电报方程
    category: physics_law
    aliases: ["传输线方程", "telegrapher equations"]
    description: 描述传输线电压电流随时间和空间的演化。

  - internal_id: impedance_matching
    display_zh: 阻抗匹配
    category: heuristic
    aliases: ["反射消除", "impedance matching"]
    description: 负载等于特征阻抗时传输线末端无反射。

  - internal_id: standing_wave_on_line
    display_zh: 传输线驻波
    category: physics_model
    aliases: ["驻波比", "line standing wave"]
    description: 入射波与反射波叠加在线路上形成驻波分布。

  - internal_id: magnetic_scalar_potential
    display_zh: 磁标势
    category: math_technique
    aliases: ["无电流区磁势", "magnetic scalar potential"]
    description: 在无自由电流区域用标势表示静磁场。

  - internal_id: vector_potential_method
    display_zh: 矢势法
    category: math_technique
    aliases: ["磁矢势", "vector potential"]
    description: 用矢势表示磁场并简化电流分布产生的场。

  - internal_id: biot_savart_integral
    display_zh: 毕奥萨伐尔积分
    category: physics_law
    aliases: ["电流元磁场", "Biot-Savart"]
    description: 对电流元积分求稳恒电流产生的磁感应强度。

  - internal_id: ampere_symmetry
    display_zh: 安培环路对称
    category: heuristic
    aliases: ["环路定理选路", "Ampere symmetry"]
    description: 选择高对称环路用安培定律快速求磁场。

  - internal_id: finite_wire_field
    display_zh: 有限长导线磁场
    category: physics_model
    aliases: ["有限直导线", "finite wire"]
    description: 有限直线电流在空间点产生与端点角相关的磁场。

  - internal_id: current_loop_field
    display_zh: 电流环磁场
    category: physics_model
    aliases: ["圆环电流", "current loop"]
    description: 圆形电流环轴线上磁场由几何积分给出。

  - internal_id: solenoid_field_model
    display_zh: 螺线管磁场
    category: physics_model
    aliases: ["长直螺线管", "solenoid"]
    description: 长螺线管内部近似匀强磁场外部近似为零。

  - internal_id: toroidal_coil_field
    display_zh: 环形线圈磁场
    category: physics_model
    aliases: ["环形螺线管", "toroid"]
    description: 环形线圈磁场主要局限于磁芯内部并呈环向分布。

  - internal_id: magnetic_field_boundary
    display_zh: 磁场边界条件
    category: physics_law
    aliases: ["B-H边界", "magnetic boundary"]
    description: 磁感应强度法向和磁场强度切向满足界面条件。

  - internal_id: surface_current_jump
    display_zh: 面电流跃变
    category: physics_law
    aliases: ["切向H跃变", "surface current"]
    description: 磁场强度切向跃变由界面自由面电流决定。

  - internal_id: magnetic_material_linear
    display_zh: 线性磁介质
    category: physics_model
    aliases: ["磁化率模型", "linear magnetic medium"]
    description: 用磁导率或磁化率描述磁介质对外磁场响应。

  - internal_id: magnetization_bound_current
    display_zh: 磁化束缚电流
    category: physics_law
    aliases: ["束缚电流", "bound current"]
    description: 非均匀磁化等效为体束缚电流和面束缚电流。

  - internal_id: uniformly_magnetized_sphere
    display_zh: 均匀磁化球
    category: physics_model
    aliases: ["磁化球", "magnetized sphere"]
    description: 均匀磁化球在外部等效为磁偶极子场。

  - internal_id: magnetic_circuit_analogy
    display_zh: 磁路类比
    category: heuristic
    aliases: ["磁阻模型", "magnetic circuit"]
    description: 用磁势差、磁通和磁阻类比电路估算磁场。

  - internal_id: air_gap_fringing
    display_zh: 气隙边缘修正
    category: approximation
    aliases: ["磁场边缘效应", "air gap fringing"]
    description: 磁路气隙处磁通扩散使有效截面积发生修正。

  - internal_id: hysteresis_loop
    display_zh: 磁滞回线
    category: physics_model
    aliases: ["B-H回线", "hysteresis loop"]
    description: 铁磁体磁化状态依赖历史并在循环中耗能。

  - internal_id: inductance_energy_method
    display_zh: 电感能量法
    category: heuristic
    aliases: ["磁场能求力", "inductor energy"]
    description: 用电感随几何变化求磁力或电磁机械能转换。

  - internal_id: mutual_inductance
    display_zh: 互感
    category: physics_law
    aliases: ["互感系数", "mutual inductance"]
    description: 一个回路电流变化在另一回路中产生感应电动势。

  - internal_id: self_inductance
    display_zh: 自感
    category: physics_law
    aliases: ["自感系数", "self inductance"]
    description: 回路自身电流变化产生反抗变化的感应电动势。

  - internal_id: inductance_matrix
    display_zh: 电感矩阵
    category: physics_model
    aliases: ["多回路互感矩阵", "inductance matrix"]
    description: 用矩阵描述多回路磁链与电流之间的线性关系。

  - internal_id: rl_transient_response
    display_zh: RL暂态响应
    category: physics_model
    aliases: ["电感暂态", "RL transient"]
    description: 电阻电感电路中电流按特征时间建立或衰减。

  - internal_id: rlc_oscillation
    display_zh: RLC振荡
    category: physics_model
    aliases: ["电磁振荡", "RLC oscillation"]
    description: 电容电场能和电感磁场能周期交换形成振荡。

  - internal_id: rlc_damping_regime
    display_zh: RLC阻尼判别
    category: math_technique
    aliases: ["欠阻尼过阻尼", "RLC damping"]
    description: 由特征方程判定电路振荡的阻尼类型。

  - internal_id: resonance_bandwidth_circuit
    display_zh: 电路共振带宽
    category: physics_law
    aliases: ["品质因数Q", "resonance bandwidth"]
    description: RLC电路共振峰宽由阻尼和品质因数决定。

  - internal_id: phasor_method
    display_zh: 相量法
    category: math_technique
    aliases: ["复阻抗法", "phasor method"]
    description: 用复数相量把正弦稳态电路转化为代数问题。

  - internal_id: complex_impedance
    display_zh: 复阻抗
    category: math_technique
    aliases: ["交流阻抗", "complex impedance"]
    description: 用复数同时表示交流元件的幅值和相位关系。

  - internal_id: ac_power_factor
    display_zh: 功率因数
    category: physics_law
    aliases: ["有功功率因数", "power factor"]
    description: 交流电路平均功率取决于电压电流相位差。

  - internal_id: transformer_model
    display_zh: 变压器模型
    category: physics_model
    aliases: ["理想变压器", "transformer"]
    description: 通过互感和磁通耦合实现交流电压电流变换。

  - internal_id: faraday_flux_rule
    display_zh: 磁通量法则
    category: physics_law
    aliases: ["法拉第定律", "flux rule"]
    description: 回路感应电动势等于穿过回路磁通量变化率的负值。

  - internal_id: motional_emf
    display_zh: 动生电动势
    category: physics_law
    aliases: ["运动电动势", "motional EMF"]
    description: 导体在磁场中运动时电荷受洛伦兹力分离产生电动势。

  - internal_id: transformer_emf
    display_zh: 感生电动势
    category: physics_law
    aliases: ["变压器电动势", "transformer EMF"]
    description: 随时间变化的磁场产生环形非保守电场。

  - internal_id: lenz_law_direction
    display_zh: 楞次定律判向
    category: heuristic
    aliases: ["感应电流方向", "Lenz law"]
    description: 感应电流方向总是反抗引起磁通变化的原因。

  - internal_id: eddy_current_damping
    display_zh: 涡流阻尼
    category: physics_model
    aliases: ["电磁阻尼", "eddy current damping"]
    description: 导体运动或变磁场中产生涡流并耗散机械能。

  - internal_id: magnetic_braking
    display_zh: 磁刹车模型
    category: physics_model
    aliases: ["电磁制动", "magnetic braking"]
    description: 导体切割磁场产生感应电流并受到反向安培力。

  - internal_id: railgun_circuit_model
    display_zh: 电磁炮轨道模型
    category: physics_model
    aliases: ["导轨炮", "railgun"]
    description: 电流导轨中的滑杆受磁力加速并耦合电路变化。

  - internal_id: sliding_rod_induction
    display_zh: 滑杆电磁感应
    category: physics_model
    aliases: ["导轨滑杆", "sliding rod"]
    description: 导体棒在磁场导轨上运动产生动生电动势和磁阻力。

  - internal_id: coupled_electromechanical_ode
    display_zh: 电机耦合方程
    category: math_technique
    aliases: ["电磁机械耦合", "coupled ODE"]
    description: 联立电路方程和运动方程求电磁驱动系统演化。

  - internal_id: quasi_static_induction
    display_zh: 准静态感应
    category: approximation
    aliases: ["低频近似", "quasi-static induction"]
    description: 尺寸远小于电磁波长时忽略辐射传播延迟。

  - internal_id: skin_effect
    display_zh: 趋肤效应
    category: physics_model
    aliases: ["集肤效应", "skin effect"]
    description: 交流电流主要集中在导体表层并随深度指数衰减。

  - internal_id: skin_depth
    display_zh: 趋肤深度
    category: physics_law
    aliases: ["集肤深度", "skin depth"]
    description: 交流电磁场进入导体后衰减到特定比例的特征深度。

  - internal_id: magnetic_diffusion
    display_zh: 磁扩散
    category: physics_model
    aliases: ["电磁扩散", "magnetic diffusion"]
    description: 导体中磁场随时间按扩散方程渗透和衰减。

  - internal_id: displacement_current
    display_zh: 位移电流
    category: physics_law
    aliases: ["麦克斯韦修正", "displacement current"]
    description: 变化电场等效产生磁场并保证电荷连续性。

  - internal_id: continuity_equation_charge
    display_zh: 电荷连续性
    category: physics_law
    aliases: ["连续性方程", "charge continuity"]
    description: 电荷密度变化率与电流散度满足局域守恒关系。

  - internal_id: maxwell_equations_integral
    display_zh: 积分麦克斯韦方程
    category: physics_law
    aliases: ["积分形式", "integral Maxwell"]
    description: 用通量和环量形式描述电磁场与源的关系。

  - internal_id: maxwell_equations_differential
    display_zh: 微分麦克斯韦方程
    category: physics_law
    aliases: ["微分形式", "differential Maxwell"]
    description: 用散度和旋度形式描述电磁场的局域规律。

  - internal_id: electromagnetic_wave_equation
    display_zh: 电磁波方程
    category: physics_law
    aliases: ["Maxwell波方程", "EM wave equation"]
    description: 无源区域中电场和磁场满足光速传播的波动方程。

  - internal_id: plane_wave_solution
    display_zh: 平面电磁波
    category: physics_model
    aliases: ["平面波", "plane EM wave"]
    description: 电磁场在均匀介质中以横波形式平面传播。

  - internal_id: polarization_state
    display_zh: 偏振态
    category: physics_model
    aliases: ["线偏振圆偏振", "polarization"]
    description: 电场矢量随时间的振动轨迹决定电磁波偏振。

  - internal_id: poynting_vector
    display_zh: 坡印廷矢量
    category: physics_law
    aliases: ["能流密度", "Poynting vector"]
    description: 电磁场能量流密度由电场与磁场叉乘给出。

  - internal_id: electromagnetic_momentum_density
    display_zh: 电磁动量密度
    category: physics_law
    aliases: ["场动量", "EM momentum"]
    description: 电磁场携带与能流相关的动量密度。

  - internal_id: radiation_pressure_wave
    display_zh: 电磁波辐射压
    category: physics_law
    aliases: ["光压", "radiation pressure"]
    description: 电磁波被吸收或反射时向物体传递动量产生压强。

  - internal_id: wave_impedance
    display_zh: 波阻抗
    category: physics_law
    aliases: ["介质阻抗", "wave impedance"]
    description: 平面波中电场与磁场振幅比由介质参数决定。

  - internal_id: fresnel_coefficients
    display_zh: 菲涅耳系数
    category: physics_law
    aliases: ["反射透射系数", "Fresnel coefficients"]
    description: 平面波在介质界面反射透射振幅由边界条件决定。

  - internal_id: brewster_angle
    display_zh: 布儒斯特角
    category: physics_model
    aliases: ["偏振角", "Brewster angle"]
    description: p偏振光在特定入射角下反射振幅为零。

  - internal_id: total_internal_reflection
    display_zh: 全反射
    category: physics_model
    aliases: ["临界角", "total internal reflection"]
    description: 从高折射率介质入射超过临界角时无传播透射波。

  - internal_id: evanescent_wave
    display_zh: 倏逝波
    category: physics_model
    aliases: ["消逝波", "evanescent wave"]
    description: 全反射界面另一侧存在沿法向指数衰减的场。

  - internal_id: waveguide_cutoff
    display_zh: 波导截止
    category: physics_model
    aliases: ["截止频率", "waveguide cutoff"]
    description: 波导模式频率低于截止值时不能传播。

  - internal_id: cavity_resonance
    display_zh: 谐振腔模式
    category: physics_model
    aliases: ["电磁腔", "cavity mode"]
    description: 导体边界内电磁场形成离散本征频率模式。

  - internal_id: mode_orthogonality
    display_zh: 模式正交性
    category: math_technique
    aliases: ["本征模正交", "mode orthogonality"]
    description: 不同本征模式在适当内积下相互正交并可展开场。

  - internal_id: boundary_value_eigenmode
    display_zh: 边值本征模
    category: math_technique
    aliases: ["边界本征值", "boundary eigenmode"]
    description: 由边界条件确定波动方程的离散空间模式。

  - internal_id: dipole_radiation_pattern
    display_zh: 偶极辐射图样
    category: physics_model
    aliases: ["电偶极辐射", "dipole radiation"]
    description: 振荡电偶极子辐射强度随方向呈特定角分布。

  - internal_id: antenna_far_field
    display_zh: 天线远场
    category: approximation
    aliases: ["辐射区场", "antenna far field"]
    description: 远离天线时只保留随距离按反比衰减的辐射场。

  - internal_id: near_field_reactive_zone
    display_zh: 近场反应区
    category: approximation
    aliases: ["感应近场", "reactive near field"]
    description: 天线附近存在不向远处输运平均能量的储能场。

  - internal_id: larmor_formula_em
    display_zh: 拉莫尔公式
    category: physics_law
    aliases: ["加速电荷辐射", "Larmor formula"]
    description: 非相对论加速电荷辐射功率正比于加速度平方。

  - internal_id: synchrotron_radiation
    display_zh: 同步辐射
    category: physics_model
    aliases: ["回旋辐射", "synchrotron radiation"]
    description: 高速带电粒子在磁场弯转运动中发出强辐射。

  - internal_id: cyclotron_motion
    display_zh: 回旋运动
    category: physics_model
    aliases: ["匀强磁场圆周运动", "cyclotron motion"]
    description: 带电粒子在匀强磁场中绕磁力线作圆周运动。

  - internal_id: helical_motion
    display_zh: 螺旋运动
    category: physics_model
    aliases: ["带电粒子螺旋线", "helical motion"]
    description: 平行磁场速度不变而垂直速度导致圆周叠加运动。

  - internal_id: crossed_field_drift
    display_zh: 叉场漂移
    category: physics_model
    aliases: ["E×B漂移", "crossed-field drift"]
    description: 带电粒子在相互垂直电磁场中出现整体漂移速度。

  - internal_id: gradient_b_drift
    display_zh: 磁场梯度漂移
    category: physics_model
    aliases: ["grad-B漂移", "gradient-B drift"]
    description: 非均匀磁场中回旋半径变化导致带电粒子横向漂移。

  - internal_id: curvature_drift
    display_zh: 曲率漂移
    category: physics_model
    aliases: ["磁力线曲率漂移", "curvature drift"]
    description: 沿弯曲磁力线运动的粒子因离心效应产生漂移。

  - internal_id: magnetic_mirror
    display_zh: 磁镜效应
    category: physics_model
    aliases: ["磁瓶", "magnetic mirror"]
    description: 粒子进入强磁场区时平行动能转为垂直动能并反射。

  - internal_id: first_adiabatic_invariant
    display_zh: 第一绝热不变量
    category: physics_law
    aliases: ["磁矩不变量", "magnetic moment invariant"]
    description: 磁场缓变时粒子垂直动能与磁场比值近似守恒。

  - internal_id: guiding_center_approximation
    display_zh: 导心近似
    category: approximation
    aliases: ["导引中心", "guiding center"]
    description: 将快速回旋平均掉只追踪粒子回旋中心运动。

  - internal_id: lorentz_force_work
    display_zh: 洛伦兹力做功
    category: physics_law
    aliases: ["磁力不做功", "Lorentz work"]
    description: 电场改变粒子能量而磁场只改变速度方向。

  - internal_id: hall_effect
    display_zh: 霍尔效应
    category: physics_model
    aliases: ["Hall effect", "霍尔电压"]
    description: 载流导体在磁场中产生横向电荷分离和电压。

  - internal_id: magnetoresistance_model
    display_zh: 磁阻模型
    category: physics_model
    aliases: ["磁电阻", "magnetoresistance"]
    description: 磁场改变载流子运动路径从而影响电阻。

  - internal_id: drude_model
    display_zh: 德鲁德模型
    category: physics_model
    aliases: ["经典电子气", "Drude model"]
    description: 将导体电子视为受碰撞阻尼的经典自由载流子。

  - internal_id: plasma_frequency
    display_zh: 等离子体频率
    category: physics_law
    aliases: ["等离子振荡", "plasma frequency"]
    description: 自由电子气相对离子背景振荡的本征频率。

  - internal_id: debye_shielding
    display_zh: 德拜屏蔽
    category: physics_model
    aliases: ["电荷屏蔽", "Debye shielding"]
    description: 等离子体中外加电荷电场在德拜长度内被屏蔽。

  - internal_id: plasma_oscillation
    display_zh: 等离子振荡
    category: physics_model
    aliases: ["Langmuir振荡", "plasma oscillation"]
    description: 电子集体偏离平衡后在静电回复力下振荡。

  - internal_id: magnetohydrodynamic_freezing
    display_zh: 磁冻结
    category: physics_model
    aliases: ["磁流体冻结", "flux freezing"]
    description: 理想导电流体中磁力线近似随流体一起运动。

  - internal_id: electromagnetic_gauge_choice
    display_zh: 电磁规范选择
    category: heuristic
    aliases: ["规范选取", "gauge choice"]
    description: 选择库仑规范或洛伦兹规范以简化电磁势方程。

  - internal_id: coulomb_gauge
    display_zh: 库仑规范
    category: physics_law
    aliases: ["横向规范", "Coulomb gauge"]
    description: 令矢势散度为零并使标势满足瞬时泊松方程。

  - internal_id: lorenz_gauge
    display_zh: 洛伦兹规范
    category: physics_law
    aliases: ["Lorenz gauge", "协变规范"]
    description: 令四维势满足洛伦兹协变规范条件以得到波方程。

  - internal_id: retarded_potential_em
    display_zh: 推迟势
    category: physics_law
    aliases: ["延迟势", "retarded potential"]
    description: 电磁势由源在满足光传播延迟的推迟时刻决定。

  - internal_id: lienard_wiechert_potential
    display_zh: 李纳维谢尔势
    category: physics_law
    aliases: ["运动点电荷势", "Liénard-Wiechert"]
    description: 任意运动点电荷产生的相对论推迟电磁势。

  - internal_id: radiation_reaction
    display_zh: 辐射反作用
    category: physics_model
    aliases: ["辐射阻尼", "radiation reaction"]
    description: 带电粒子辐射能量后受到与自身场相关的反作用。

  - internal_id: abraham_lorentz_force
    display_zh: 亚伯拉罕洛伦兹力
    category: physics_law
    aliases: ["自力", "Abraham-Lorentz force"]
    description: 非相对论辐射反作用力与加速度时间导数有关。

  - internal_id: electromagnetic_mass
    display_zh: 电磁质量
    category: physics_model
    aliases: ["场能质量", "electromagnetic mass"]
    description: 电荷自身电磁场能量可表现为惯性质量贡献。

  - internal_id: field_momentum_paradox
    display_zh: 场动量佯谬
    category: physics_model
    aliases: ["隐藏动量", "field momentum paradox"]
    description: 静态电磁系统中场动量需与机械隐藏动量共同守恒。

  - internal_id: hidden_momentum
    display_zh: 隐藏动量
    category: physics_model
    aliases: ["机械隐藏动量", "hidden momentum"]
    description: 稳恒电流体系中内部能流可产生不可见机械动量。

  - internal_id: electromagnetic_angular_momentum
    display_zh: 电磁角动量
    category: physics_law
    aliases: ["场角动量", "EM angular momentum"]
    description: 电磁场携带由位置矢量和场动量密度决定的角动量。

  - internal_id: feynman_disk_paradox
    display_zh: 费曼圆盘佯谬
    category: physics_model
    aliases: ["场角动量转移", "Feynman disk"]
    description: 电磁场角动量在磁场消失时转化为机械角动量。

  - internal_id: coaxial_cable_field_energy
    display_zh: 同轴线场能流
    category: physics_model
    aliases: ["同轴电缆能流", "coaxial cable"]
    description: 同轴电缆中能量主要通过导体间电磁场输运。

  - internal_id: poynting_theorem
    display_zh: 坡印廷定理
    category: physics_law
    aliases: ["电磁能量守恒", "Poynting theorem"]
    description: 电磁能量变化、能流和对电荷做功满足局域守恒。

  - internal_id: boundary_layer_current
    display_zh: 表面电流层
    category: approximation
    aliases: ["薄电流层", "surface current layer"]
    description: 将薄导电区域中的电流近似压缩为面电流处理。

  - internal_id: perfect_conductor_boundary
    display_zh: 理想导体边界
    category: physics_model
    aliases: ["完全导体", "perfect conductor"]
    description: 理想导体内部电场为零并约束边界处场分量。

  - internal_id: superconductor_meissner
    display_zh: 迈斯纳效应
    category: physics_model
    aliases: ["超导抗磁", "Meissner effect"]
    description: 超导体排斥内部磁场并在表面形成屏蔽电流。

  - internal_id: london_equation
    display_zh: 伦敦方程
    category: physics_law
    aliases: ["London equation", "超导电流方程"]
    description: 描述超导电流与磁场穿透深度关系的经验方程。

  - internal_id: magnetic_flux_quantization
    display_zh: 磁通量量子化
    category: physics_law
    aliases: ["flux quantum", "磁通量子"]
    description: 超导环中磁通以普朗克常量和电荷确定的单位量子化。

  - internal_id: dipole_torque_precession
    display_zh: 磁偶极进动
    category: physics_model
    aliases: ["拉莫尔进动", "dipole precession"]
    description: 磁偶极矩在外磁场中受力矩并绕磁场方向进动。

  - internal_id: larmor_precession
    display_zh: 拉莫尔进动
    category: physics_law
    aliases: ["Larmor precession", "磁矩进动"]
    description: 带磁矩粒子在外磁场中以拉莫尔频率进动。

  - internal_id: stern_gerlach_force
    display_zh: 斯特恩盖拉赫力
    category: physics_model
    aliases: ["磁矩梯度力", "Stern-Gerlach"]
    description: 非均匀磁场对磁偶极矩产生与取向有关的力。

  - internal_id: electric_quadrupole_field
    display_zh: 电四极场
    category: physics_model
    aliases: ["四极矩场", "electric quadrupole"]
    description: 总电荷和偶极矩为零时远场主项可能为四极项。

  - internal_id: quadrupole_trap_model
    display_zh: 四极阱模型
    category: physics_model
    aliases: ["Paul阱", "quadrupole trap"]
    description: 用四极电场或时变场实现带电粒子约束。

  - internal_id: penning_trap_model
    display_zh: 彭宁阱模型
    category: physics_model
    aliases: ["Penning trap", "电磁阱"]
    description: 用静电四极势和恒定磁场束缚带电粒子。

  - internal_id: paul_trap_pseudopotential
    display_zh: 保罗阱赝势
    category: approximation
    aliases: ["射频赝势", "Paul trap pseudopotential"]
    description: 高频交变四极场平均后形成约束粒子的有效势。

  - internal_id: mathieu_stability_em
    display_zh: 马 Mathieu 稳定区
    category: math_technique
    aliases: ["Mathieu stability", "参数稳定"]
    description: 带电粒子在周期场中的稳定性由Mathieu方程决定。

  - internal_id: small_signal_linearization
    display_zh: 小信号线性化
    category: approximation
    aliases: ["微扰线性化", "small-signal"]
    description: 在稳定工作点附近将非线性电路或场方程线性化。

  - internal_id: slowly_varying_envelope_em
    display_zh: 慢变包络近似
    category: approximation
    aliases: ["SVEA", "slowly varying envelope"]
    description: 波幅相对载波周期变化缓慢时忽略高阶导数项。

  - internal_id: paraxial_wave_approximation
    display_zh: 近轴波近似
    category: approximation
    aliases: ["近轴近似", "paraxial approximation"]
    description: 波主要沿轴向传播且横向变化缓慢时简化波方程。

  - internal_id: gaussian_beam_model
    display_zh: 高斯光束模型
    category: physics_model
    aliases: ["Gaussian beam", "TEM00光束"]
    description: 近轴电磁波的基模具有高斯横向强度分布。

  - internal_id: diffraction_integral
    display_zh: 衍射积分
    category: math_technique
    aliases: ["惠更斯积分", "diffraction integral"]
    description: 用孔径面上波源叠加计算远近场衍射图样。

  - internal_id: fraunhofer_diffraction
    display_zh: 夫琅禾费衍射
    category: approximation
    aliases: ["远场衍射", "Fraunhofer diffraction"]
    description: 远场条件下衍射振幅近似为孔径函数傅里叶变换。

  - internal_id: fresnel_diffraction
    display_zh: 菲涅耳衍射
    category: approximation
    aliases: ["近场衍射", "Fresnel diffraction"]
    description: 近场条件下保留传播相位的二次项计算衍射。

  - internal_id: fourier_optics
    display_zh: 傅里叶光学
    category: math_technique
    aliases: ["空间频谱", "Fourier optics"]
    description: 用傅里叶变换描述孔径、透镜和衍射传播关系。

  - internal_id: polarization_jones_vector
    display_zh: 琼斯矢量
    category: math_technique
    aliases: ["Jones vector", "偏振矢量"]
    description: 用复二维矢量表示完全偏振光的振幅和相位。

  - internal_id: birefringence_phase_delay
    display_zh: 双折射相延迟
    category: physics_model
    aliases: ["波片相位差", "birefringence"]
    description: 各向异性介质中两正交偏振传播相速不同产生相位差。

  - internal_id: malus_law
    display_zh: 马吕斯定律
    category: physics_law
    aliases: ["偏振片定律", "Malus law"]
    description: 线偏振光透过偏振片强度按夹角余弦平方变化。

  - internal_id: electromagnetic_duality
    display_zh: 电磁对偶
    category: heuristic
    aliases: ["E-B对偶", "EM duality"]
    description: 利用电场磁场方程结构相似性类比构造解。

  - internal_id: dimensional_analysis_em
    display_zh: 电磁量纲分析
    category: heuristic
    aliases: ["电磁标度估算", "EM dimensional analysis"]
    description: 用量纲和特征尺度估算场强、能量或时间尺度。

  - internal_id: dominant_balance_em
    display_zh: 电磁主导平衡
    category: heuristic
    aliases: ["量级平衡", "EM dominant balance"]
    description: 比较电场、磁场、阻尼和惯性项确定主导物理过程。

  - internal_id: asymptotic_field_region
    display_zh: 场区渐近划分
    category: heuristic
    aliases: ["近场远场划分", "field regions"]
    description: 按距离或频率将问题分为近场、感应区和辐射区。

  - internal_id: small_gap_approximation
    display_zh: 小间隙近似
    category: approximation
    aliases: ["局部平行板", "small gap"]
    description: 间隙远小于曲率半径时局部按平行板场处理。

  - internal_id: long_solenoid_approximation
    display_zh: 长螺线管近似
    category: approximation
    aliases: ["忽略端部场", "long solenoid"]
    description: 螺线管长度远大于半径时内部场近似均匀。

  - internal_id: infinite_plane_approximation
    display_zh: 无限平面近似
    category: approximation
    aliases: ["局部无限面", "infinite plane"]
    description: 观察尺度远小于边界尺寸时将有限面视作无限大。

  - internal_id: dipole_approximation
    display_zh: 偶极近似
    category: approximation
    aliases: ["长波偶极近似", "dipole approximation"]
    description: 源尺寸远小于观察距离或波长时仅保留偶极项。

  - internal_id: radiation_zone_approximation
    display_zh: 辐射区近似
    category: approximation
    aliases: ["远区近似", "radiation zone"]
    description: 远离源时只保留横向且随距离反比衰减的辐射场。

  - internal_id: quasi_neutral_approximation
    display_zh: 准中性近似
    category: approximation
    aliases: ["等离子准中性", "quasi-neutral"]
    description: 大尺度等离子体中正负电荷密度近似相等。

  - internal_id: perfect_dielectric_approximation
    display_zh: 理想介质近似
    category: approximation
    aliases: ["无损介质", "perfect dielectric"]
    description: 忽略介质电导和损耗，只考虑介电极化响应。

  - internal_id: perfect_magnetic_conductor
    display_zh: 理想磁导体边界
    category: physics_model
    aliases: ["PMC边界", "perfect magnetic conductor"]
    description: 理想化边界条件中磁场切向分量为零。

  - internal_id: superconducting_image_current
    display_zh: 超导镜像电流
    category: heuristic
    aliases: ["磁镜像法", "image current"]
    description: 用镜像电流或磁偶极处理超导平面的磁场排斥。

  - internal_id: electric_field_line_mapping
    display_zh: 电力线映射
    category: heuristic
    aliases: ["场线几何", "field-line mapping"]
    description: 通过电力线密度和方向判断电场结构与边界感应。

  - internal_id: equipotential_surface_method
    display_zh: 等势面法
    category: heuristic
    aliases: ["等势面构造", "equipotential method"]
    description: 利用等势面与电场垂直关系构造或检验电势解。

  - internal_id: reciprocal_theorem_electrostatics
    display_zh: 静电互易定理
    category: physics_law
    aliases: ["格林互易", "reciprocity theorem"]
    description: 两组静电源场之间满足互易积分关系。

  - internal_id: lorentz_reciprocity
    display_zh: 洛伦兹互易
    category: physics_law
    aliases: ["电磁互易定理", "Lorentz reciprocity"]
    description: 线性互易介质中两组源场响应满足互易关系。

  - internal_id: variational_capacitance_bound
    display_zh: 电容变分估计
    category: math_technique
    aliases: ["变分界限", "capacitance variational"]
    description: 用试探电势或试探电荷分布估计电容上下界。

  - internal_id: conformal_capacitance
    display_zh: 保角电容计算
    category: math_technique
    aliases: ["二维电容保角法", "conformal capacitance"]
    description: 通过保角映射把复杂二维电容问题化为简单几何。

  - internal_id: singular_edge_field
    display_zh: 边缘奇异场
    category: physics_model
    aliases: ["尖端场增强", "edge singularity"]
    description: 导体尖端或边缘附近电场可能出现幂律增强。

  - internal_id: corona_threshold
    display_zh: 电晕阈值
    category: physics_model
    aliases: ["击穿起始", "corona threshold"]
    description: 尖端或高压导线附近场强超过阈值时空气电离。

  - internal_id: dielectric_breakdown
    display_zh: 介质击穿
    category: physics_model
    aliases: ["击穿场强", "dielectric breakdown"]
    description: 电场超过材料耐受强度时介质由绝缘转为导通。

  - internal_id: charged_drop_rayleigh_limit
    display_zh: 带电液滴极限
    category: physics_model
    aliases: ["瑞利极限", "Rayleigh limit"]
    description: 静电排斥超过表面张力时带电液滴发生失稳分裂。

  - internal_id: electroscope_force_balance
    display_zh: 验电器力平衡
    category: physics_model
    aliases: ["电斥力平衡", "electroscope"]
    description: 带电薄片或小球在静电斥力和重力下达到平衡。

  - internal_id: charged_particle_energy_analyzer
    display_zh: 带电粒子能谱仪
    category: physics_model
    aliases: ["电磁分析器", "energy analyzer"]
    description: 用电场或磁场偏转半径筛选带电粒子能量。

  - internal_id: mass_spectrometer_model
    display_zh: 质谱仪模型
    category: physics_model
    aliases: ["质谱分析", "mass spectrometer"]
    description: 带电粒子经电磁场筛选后按荷质比分离。

  - internal_id: velocity_selector
    display_zh: 速度选择器
    category: physics_model
    aliases: ["E-B速度选择", "velocity selector"]
    description: 交叉电磁场中只有特定速度粒子能直线通过。

  - internal_id: cyclotron_resonance
    display_zh: 回旋共振
    category: physics_model
    aliases: ["cyclotron resonance", "回旋加速"]
    description: 交流电场频率匹配回旋频率时持续加速粒子。

  - internal_id: betatron_acceleration
    display_zh: 电子感应加速
    category: physics_model
    aliases: ["Betatron", "感应加速器"]
    description: 变化磁通产生环形电场使电子沿圆轨道加速。

  - internal_id: betatron_condition
    display_zh: Betatron条件
    category: physics_law
    aliases: ["二倍场条件", "betatron condition"]
    description: 轨道处磁场与平均磁场满足关系以保持圆轨稳定。

  - internal_id: magnetic_pressure
    display_zh: 磁压
    category: physics_law
    aliases: ["磁场压强", "magnetic pressure"]
    description: 磁场具有与磁感应强度平方相关的等效压强。

  - internal_id: magnetic_tension
    display_zh: 磁张力
    category: physics_law
    aliases: ["磁力线张力", "magnetic tension"]
    description: 弯曲磁力线表现出沿磁力线方向拉直的张力效应。

  - internal_id: pinch_effect
    display_zh: 箍缩效应
    category: physics_model
    aliases: ["Z箍缩", "pinch effect"]
    description: 电流自身磁场对载流等离子体产生向内压缩力。

  - internal_id: force_on_current_loop
    display_zh: 电流环受力
    category: physics_law
    aliases: ["磁偶极受力", "current loop force"]
    description: 非均匀磁场中电流环受到与磁矩梯度相关的力。

  - internal_id: torque_on_current_loop
    display_zh: 电流环力矩
    category: physics_law
    aliases: ["磁偶极力矩", "current loop torque"]
    description: 电流环磁矩在外磁场中受到使其取向对齐的力矩。

  - internal_id: rail_contact_resistance
    display_zh: 导轨接触电阻
    category: approximation
    aliases: ["接触电阻修正", "contact resistance"]
    description: 电磁机械导轨问题中可将接触耗散等效为附加电阻。

  - internal_id: finite_conductivity_correction
    display_zh: 有限电导修正
    category: approximation
    aliases: ["非理想导体修正", "finite conductivity"]
    description: 导体电导率有限时内部电场和焦耳热不能忽略。

  - internal_id: joule_heating_balance
    display_zh: 焦耳热平衡
    category: physics_law
    aliases: ["电热功率", "Joule heating"]
    description: 电流通过电阻产生的热功率等于电流平方乘电阻。

  - internal_id: thermal_electrical_feedback
    display_zh: 电热反馈
    category: physics_model
    aliases: ["温阻耦合", "electrothermal feedback"]
    description: 电阻随温度变化使电流发热与散热过程相互耦合。

  - internal_id: nonlinear_resistor_model
    display_zh: 非线性电阻模型
    category: physics_model
    aliases: ["伏安非线性", "nonlinear resistor"]
    description: 电压电流关系非线性时需由伏安曲线和电路方程联立。

  - internal_id: diode_exponential_law
    display_zh: 二极管指数律
    category: physics_model
    aliases: ["Shockley方程", "diode law"]
    description: 二极管电流随正向电压近似指数增长。

  - internal_id: small_signal_equivalent_circuit
    display_zh: 小信号等效电路
    category: heuristic
    aliases: ["线性化等效", "small-signal circuit"]
    description: 在工作点附近用等效线性元件描述非线性器件响应。

  - internal_id: electrostatic_force_inverse_problem
    display_zh: 静电力反推
    category: math_technique
    aliases: ["由力反推场", "force inverse problem"]
    description: 根据带电体受力或平衡条件反推电荷或场分布。

  - internal_id: current_density_distribution
    display_zh: 电流密度分布
    category: physics_model
    aliases: ["J分布", "current density"]
    description: 在导体或介质中求空间非均匀电流密度分布。

  - internal_id: anisotropic_conductivity
    display_zh: 各向异性电导
    category: physics_model
    aliases: ["电导张量", "anisotropic conductivity"]
    description: 电流密度与电场通过张量关系相连而非同向。

  - internal_id: anisotropic_dielectric
    display_zh: 各向异性介质
    category: physics_model
    aliases: ["介电张量", "anisotropic dielectric"]
    description: 电位移与电场在晶体中可由介电张量联系。

  - internal_id: effective_medium_approximation
    display_zh: 有效介质近似
    category: approximation
    aliases: ["等效介电常数", "effective medium"]
    description: 将微观混合结构近似为宏观均匀介质参数。

  - internal_id: homogenization_method
    display_zh: 均匀化方法
    category: approximation
    aliases: ["等效参数", "homogenization"]
    description: 多尺度结构中用平均场求等效电磁材料参数。

  - internal_id: perturbative_boundary_deformation
    display_zh: 边界微扰
    category: approximation
    aliases: ["形状微扰", "boundary perturbation"]
    description: 边界形状小变形时按扰动量求场和能量修正。

  - internal_id: small_hole_perturbation
    display_zh: 小孔微扰
    category: approximation
    aliases: ["小孔场修正", "small aperture"]
    description: 孔径远小于尺度或波长时将其作为小扰动处理。

  - internal_id: induced_charge_conservation
    display_zh: 感应电荷守恒
    category: heuristic
    aliases: ["总感应电荷", "induced charge conservation"]
    description: 孤立导体总电荷固定，接地导体可与地交换电荷。

  - internal_id: charge_sharing_equal_potential
    display_zh: 等势分电荷
    category: heuristic
    aliases: ["导体连接分荷", "charge sharing"]
    description: 导体相连后电势相等并按电容重新分配电荷。

  - internal_id: floating_conductor_condition
    display_zh: 孤立导体条件
    category: physics_model
    aliases: ["浮置导体", "floating conductor"]
    description: 孤立导体总电荷固定而表面电势为未知常数。

  - internal_id: grounded_vs_isolated_choice
    display_zh: 接地孤立判别
    category: heuristic
    aliases: ["导体边界判别", "grounded isolated"]
    description: 先判断导体能否与外界交换电荷以设定边界条件。

  - internal_id: moving_boundary_emf
    display_zh: 运动边界电动势
    category: heuristic
    aliases: ["变回路磁通", "moving boundary EMF"]
    description: 回路形状变化时同时考虑磁通变化和动生项。

  - internal_id: sign_convention_induction
    display_zh: 感应符号约定
    category: heuristic
    aliases: ["正方向约定", "induction sign"]
    description: 先规定回路方向和磁通正向以避免电动势符号混乱。

  - internal_id: piecewise_circuit_switching
    display_zh: 分段开关电路
    category: heuristic
    aliases: ["开关暂态分段", "piecewise switching"]
    description: 开关状态改变后重新确定初值并分段求解暂态过程。

  - internal_id: capacitor_voltage_continuity
    display_zh: 电容电压连续
    category: physics_law
    aliases: ["电容初值", "capacitor continuity"]
    description: 有限电流下电容电压不能在瞬间突变。

  - internal_id: inductor_current_continuity
    display_zh: 电感电流连续
    category: physics_law
    aliases: ["电感初值", "inductor continuity"]
    description: 有限电压下电感电流不能在瞬间突变。

  - internal_id: impulse_voltage_current
    display_zh: 冲激电压电流
    category: math_technique
    aliases: ["δ函数源", "impulse source"]
    description: 用冲激函数描述理想开关瞬间的电压或电流变化。

  - internal_id: laplace_transform_circuit
    display_zh: 拉普拉斯变换电路
    category: math_technique
    aliases: ["s域电路", "Laplace circuit"]
    description: 将线性暂态电路化为代数形式并处理初始条件。

  - internal_id: frequency_response
    display_zh: 频率响应
    category: math_technique
    aliases: ["传递函数", "frequency response"]
    description: 用输入输出复振幅比描述线性系统对不同频率的响应。

  - internal_id: filter_cutoff_frequency
    display_zh: 滤波截止频率
    category: physics_model
    aliases: ["低通高通", "cutoff frequency"]
    description: 电路滤波器在特征频率附近改变信号幅相响应。

  - internal_id: resonance_phase_analysis
    display_zh: 共振相位分析
    category: heuristic
    aliases: ["相位判据", "resonance phase"]
    description: 用电压电流相位关系判断共振和能量交换机制。

  - internal_id: electromagnetic_similarity_scaling
    display_zh: 电磁相似标度
    category: heuristic
    aliases: ["缩放律", "EM scaling"]
    description: 改变几何尺寸和材料参数时用标度关系推断结果。

  - internal_id: limiting_case_check_em
    display_zh: 电磁极限校验
    category: heuristic
    aliases: ["极限检验", "EM limiting case"]
    description: 用介电常数趋零无穷、频率趋零等极限检验解。

  - internal_id: field_superposition_strategy
    display_zh: 场叠加策略
    category: heuristic
    aliases: ["叠加拆解", "field superposition"]
    description: 将复杂源分解为简单源并线性叠加电磁场。

  - internal_id: reciprocal_problem_mapping
    display_zh: 互易问题映射
    category: heuristic
    aliases: ["互易换源", "reciprocal mapping"]
    description: 交换源点和观测点以简化线性电磁响应计算。

  - internal_id: symmetry_axis_expansion
    display_zh: 对称轴展开
    category: math_technique
    aliases: ["轴上场展开", "axis expansion"]
    description: 先求对称轴上场再用展开或边界条件推断邻域场。

  - internal_id: local_field_approximation
    display_zh: 局域场近似
    category: approximation
    aliases: ["局部均匀场", "local field"]
    description: 源或物体尺度远小于场变化尺度时外场视作均匀。

  - internal_id: perturbative_force_from_energy
    display_zh: 能量微扰求力
    category: approximation
    aliases: ["小位移求力", "force from energy"]
    description: 对能量关于位移作小量展开并求导得到近似力。

  - internal_id: induced_emf_energy_balance
    display_zh: 感应能量平衡
    category: heuristic
    aliases: ["机械功电热平衡", "induction energy"]
    description: 电磁感应系统中机械功转化为电能或焦耳热。

  - internal_id: moving_charge_field_transform
    display_zh: 运动电荷场变换
    category: physics_law
    aliases: ["运动电荷电磁场", "moving charge field"]
    description: 由静止电荷电场经洛伦兹变换得到运动电荷场。

  - internal_id: current_wire_relativity
    display_zh: 载流导线相对论
    category: physics_model
    aliases: ["电磁力相对论解释", "current wire relativity"]
    description: 用不同参考系电荷密度变化解释电流间磁力。

  - internal_id: field_tensor_transform
    display_zh: 电磁场张量变换
    category: physics_law
    aliases: ["Fμν变换", "field tensor"]
    description: 用反对称场张量统一描述电场磁场的洛伦兹变换。

  - internal_id: electromagnetic_invariants
    display_zh: 电磁场不变量
    category: physics_law
    aliases: ["场不变量", "EM invariants"]
    description: 电磁场的两个洛伦兹不变量用于分类场型。

  - internal_id: pure_electric_frame
    display_zh: 纯电场系
    category: heuristic
    aliases: ["消磁场参考系", "pure electric frame"]
    description: 当场不变量条件允许时选取参考系使磁场消失。

  - internal_id: pure_magnetic_frame
    display_zh: 纯磁场系
    category: heuristic
    aliases: ["消电场参考系", "pure magnetic frame"]
    description: 当场不变量条件允许时选取参考系使电场消失。

  - internal_id: covariant_lorentz_force
    display_zh: 协变洛伦兹力
    category: physics_law
    aliases: ["四维洛伦兹力", "covariant Lorentz force"]
    description: 用四速度和电磁场张量表示带电粒子受力方程。

  - internal_id: relativistic_particle_in_field
    display_zh: 相对论带电粒子
    category: physics_model
    aliases: ["高速粒子电磁运动", "relativistic charged particle"]
    description: 高速带电粒子在电磁场中的运动需使用相对论动量。

  - internal_id: drift_frame_transform
    display_zh: 漂移参考系
    category: heuristic
    aliases: ["消电场换系", "drift frame"]
    description: 在交叉电磁场中换到使电场消失的参考系求运动。

  - internal_id: magnetic_force_between_currents
    display_zh: 电流间磁力
    category: physics_law
    aliases: ["平行电流力", "force between currents"]
    description: 平行电流因各自产生的磁场而相互吸引或排斥。

  - internal_id: current_sheet_field
    display_zh: 电流片磁场
    category: physics_model
    aliases: ["面电流磁场", "current sheet"]
    description: 无限面电流两侧产生大小相等方向相反的匀强磁场。

  - internal_id: charged_sheet_field
    display_zh: 带电面电场
    category: physics_model
    aliases: ["无限带电面", "charged sheet"]
    description: 无限均匀带电平面两侧产生大小恒定的电场。

  - internal_id: poisson_boltzmann_equation
    display_zh: 泊松玻尔兹曼方程
    category: math_technique
    aliases: ["PB方程", "Poisson-Boltzmann"]
    description: 将电势泊松方程与热平衡粒子分布联立求屏蔽场。

  - internal_id: exponential_screening
    display_zh: 指数屏蔽
    category: approximation
    aliases: ["屏蔽势", "exponential screening"]
    description: 在弱势近似下电势随距离按指数衰减。

  - internal_id: small_potential_linearization
    display_zh: 小电势线性化
    category: approximation
    aliases: ["Debye-Huckel近似", "small potential"]
    description: 电势能远小于热能时对玻尔兹曼因子线性展开。

  - internal_id: charge_density_wave
    display_zh: 电荷密度波
    category: physics_model
    aliases: ["密度振荡", "charge density wave"]
    description: 电荷密度空间周期调制并与电场或晶格耦合。

  - internal_id: coulomb_gas_model
    display_zh: 库仑气体模型
    category: physics_model
    aliases: ["Coulomb gas", "电荷气体"]
    description: 多个正负电荷通过库仑作用组成的统计模型。

  - internal_id: green_reciprocity_energy
    display_zh: 格林互易能量
    category: heuristic
    aliases: ["互易求能", "Green reciprocity"]
    description: 利用互易关系把难求源场能量转化为易求辅助问题。

  - internal_id: force_density_j_cross_b
    display_zh: 磁力密度
    category: physics_law
    aliases: ["J×B力", "Lorentz force density"]
    description: 连续电流分布在磁场中的力密度为电流密度叉乘磁场。

  - internal_id: electric_force_density
    display_zh: 电力密度
    category: physics_law
    aliases: ["ρE力", "electric force density"]
    description: 连续电荷分布在电场中受到与电荷密度成正比的力密度。

  - internal_id: ponderomotive_force
    display_zh: 有质动力
    category: physics_model
    aliases: ["Ponderomotive force", "高频场平均力"]
    description: 带电粒子在非均匀高频电磁场中受到平均排斥力。

  - internal_id: time_averaged_em_force
    display_zh: 时均电磁力
    category: approximation
    aliases: ["周期平均力", "time-averaged force"]
    description: 对快速振荡场的力在周期上平均得到慢变效果。

  - internal_id: electrostatic_actuator_pullin
    display_zh: 静电吸合失稳
    category: physics_model
    aliases: ["pull-in instability", "电容吸合"]
    description: 静电力随间隙增大导致弹性支撑系统突然吸合。

  - internal_id: mems_parallel_plate
    display_zh: MEMS平板模型
    category: physics_model
    aliases: ["微机电电容", "MEMS capacitor"]
    description: 可移动平行板电容中电场力与弹性力耦合。

  - internal_id: dielectric_force_in_capacitor
    display_zh: 介质吸入力
    category: physics_model
    aliases: ["电容吸介质", "dielectric insertion"]
    description: 介质被吸入电容器以增大电容并降低系统能量。

  - internal_id: magnetic_susceptibility_force
    display_zh: 磁化率受力
    category: physics_model
    aliases: ["磁介质受力", "susceptibility force"]
    description: 磁化率非零物体在非均匀磁场中受到梯度力。

  - internal_id: diamagnetic_levitation
    display_zh: 抗磁悬浮
    category: physics_model
    aliases: ["diamagnetic levitation", "抗磁力"]
    description: 抗磁材料在强非均匀磁场中可由磁力平衡重力。

  - internal_id: paramagnetic_attraction
    display_zh: 顺磁吸引
    category: physics_model
    aliases: ["paramagnetic force", "顺磁力"]
    description: 顺磁材料被吸向磁场更强区域并降低磁能。

  - internal_id: eddy_current_repulsion
    display_zh: 涡流排斥
    category: physics_model
    aliases: ["感应排斥", "eddy repulsion"]
    description: 快变磁场在导体中激发涡流并产生反抗磁通变化的力。

  - internal_id: magnetic_levitation_induction
    display_zh: 感应磁悬浮
    category: physics_model
    aliases: ["交流磁悬浮", "induction levitation"]
    description: 交流磁场诱导导体涡流产生平均向上的排斥力。

  - internal_id: field_energy_partition
    display_zh: 场能分区
    category: heuristic
    aliases: ["能量区域积分", "field energy partition"]
    description: 将空间分区积分电磁能量以处理分段介质或边界。

  - internal_id: stress_tensor_surface_choice
    display_zh: 应力面选择
    category: heuristic
    aliases: ["积分面选择", "stress surface"]
    description: 选择方便闭合曲面用麦克斯韦应力张量求总力。

  - internal_id: gaussian_surface_choice
    display_zh: 高斯面选择
    category: heuristic
    aliases: ["选高斯面", "Gaussian surface"]
    description: 根据对称性选择曲面使通量积分简化求场。

  - internal_id: amperian_loop_choice
    display_zh: 安培环路选择
    category: heuristic
    aliases: ["选安培环路", "Amperian loop"]
    description: 根据电流和磁场对称性选择环路简化环量积分。

  - internal_id: superposition_with_uniform_field
    display_zh: 叠加匀强场
    category: heuristic
    aliases: ["外场叠加", "uniform field superposition"]
    description: 将局域源场与匀强外场叠加满足边界或远场条件。

  - internal_id: equivalent_surface_charge
    display_zh: 等效面电荷
    category: heuristic
    aliases: ["束缚面电荷", "equivalent surface charge"]
    description: 用表面电荷分布等效表示极化或导体边界效果。

  - internal_id: equivalent_surface_current
    display_zh: 等效面电流
    category: heuristic
    aliases: ["束缚面电流", "equivalent surface current"]
    description: 用表面电流分布等效表示磁化或边界磁场跃变。

  - internal_id: multipole_selection_by_symmetry
    display_zh: 对称性选多极
    category: heuristic
    aliases: ["多极项判零", "multipole symmetry"]
    description: 利用电荷分布对称性判断哪些多极矩必定为零。

  - internal_id: leading_order_far_field
    display_zh: 远场主导项
    category: approximation
    aliases: ["主多极项", "leading far field"]
    description: 在远距离只保留衰减最慢的非零多极场项。

  - internal_id: near_axis_expansion
    display_zh: 近轴展开
    category: approximation
    aliases: ["轴附近展开", "near-axis expansion"]
    description: 在对称轴附近按横向距离展开场量求近似运动。

  - internal_id: paraxial_particle_focusing
    display_zh: 近轴粒子聚焦
    category: physics_model
    aliases: ["电磁透镜", "paraxial focusing"]
    description: 近轴带电粒子在电磁场中受线性回复力形成聚焦。

  - internal_id: quadrupole_focusing
    display_zh: 四极聚焦
    category: physics_model
    aliases: ["四极磁铁", "quadrupole focusing"]
    description: 四极场对一个横向方向聚焦而对另一个方向散焦。

  - internal_id: alternating_gradient_focusing
    display_zh: 交变梯度聚焦
    category: physics_model
    aliases: ["强聚焦", "alternating gradient"]
    description: 交替排列聚焦散焦元件实现整体稳定束流传输。

  - internal_id: envelope_equation_beam
    display_zh: 束包络方程
    category: math_technique
    aliases: ["beam envelope", "包络方程"]
    description: 描述粒子束横向尺寸随传播距离变化的微分方程。

  - internal_id: space_charge_effect
    display_zh: 空间电荷效应
    category: physics_model
    aliases: ["束流自场", "space charge"]
    description: 带电粒子束自身电场影响束流扩展和聚焦。

  - internal_id: child_langmuir_law
    display_zh: Child-Langmuir定律
    category: physics_law
    aliases: ["空间电荷限制流", "Child law"]
    description: 平行板真空二极管的空间电荷限制电流满足三分之二律。

  - internal_id: thermionic_emission
    display_zh: 热电子发射
    category: physics_model
    aliases: ["Richardson定律", "thermionic emission"]
    description: 金属中电子热激发越过逸出功形成发射电流。

  - internal_id: field_emission
    display_zh: 场致发射
    category: physics_model
    aliases: ["隧穿发射", "field emission"]
    description: 强电场降低势垒使电子通过量子隧穿逸出表面。

  - internal_id: photoelectric_current_model
    display_zh: 光电流模型
    category: physics_model
    aliases: ["光电效应电路", "photoelectric current"]
    description: 光照产生电子发射并在外电场中形成可测电流。

  - internal_id: retarding_potential_method
    display_zh: 遏止电势法
    category: heuristic
    aliases: ["截止电压", "retarding potential"]
    description: 用反向电压截止光电子以测量最大动能。

  - internal_id: magnetic_vector_potential_phase
    display_zh: 矢势相位效应
    category: physics_model
    aliases: ["Aharonov-Bohm", "AB效应"]
    description: 即使磁场为零区域，矢势也可影响带电粒子相位。

  - internal_id: electromagnetic_boundary_work
    display_zh: 边界移动做功
    category: heuristic
    aliases: ["场-机械功转换", "boundary work"]
    description: 电磁边界移动时场能变化与机械功和源功共同平衡。