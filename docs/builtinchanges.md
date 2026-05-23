version: "v0.1"
tags:
  - internal_id: fermat_principle
    display_zh: 费马原理
    category: physics_law
    aliases: ["最短光程原理", "光程平稳原理", "Fermat principle"]
    description: 用光程平稳条件确定真实光路。

  - internal_id: optical_path_stationarity
    display_zh: 光程平稳
    category: heuristic
    aliases: ["光程极值", "等光程", "OPL stationarity"]
    description: 将成像或传播问题转化为光程变分。

  - internal_id: snell_law
    display_zh: 折射定律
    category: physics_law
    aliases: ["斯涅尔定律", "Snell定律", "n sin theta"]
    description: 用界面两侧折射角联系折射率。

  - internal_id: reflection_law
    display_zh: 反射定律
    category: physics_law
    aliases: ["镜面反射", "入射角等于反射角", "law of reflection"]
    description: 用入射角等于反射角确定反射光线。

  - internal_id: total_internal_reflection
    display_zh: 全反射
    category: physics_law
    aliases: ["临界角", "TIR", "全内反射"]
    description: 判断光线在高折射率侧是否完全反射。

  - internal_id: wave_vector_boundary
    display_zh: 波矢边界条件
    category: physics_law
    aliases: ["切向波矢守恒", "相位匹配", "k_parallel守恒"]
    description: 用界面切向波矢连续推导反射折射。

  - internal_id: gradient_index_ray
    display_zh: 变折射率光线
    category: physics_law
    aliases: ["GRIN光线", "梯度折射率", "不均匀介质光线"]
    description: 描述折射率梯度导致的光线弯曲。

  - internal_id: cylindrical_index_invariant
    display_zh: 柱对称不变量
    category: physics_law
    aliases: ["柱坐标守恒量", "光纤不变量", "nr cos theta"]
    description: 利用柱对称折射率得到光线守恒量。

  - internal_id: spherical_index_invariant
    display_zh: 球对称不变量
    category: physics_law
    aliases: ["nr sin phi", "球对称光线守恒", "Bouguer invariant"]
    description: 在球对称介质中使用角动量型守恒量。

  - internal_id: optical_mechanical_analogy
    display_zh: 光力类比
    category: heuristic
    aliases: ["光学力学类比", "最小作用量类比", "Hamilton类比"]
    description: 将光线传播类比为力学轨道问题。

  - internal_id: effective_potential
    display_zh: 有效势
    category: physics_model
    aliases: ["等效势能", "径向有效势", "effective potential"]
    description: 用径向有效势分析稳定轨道和转向点。

  - internal_id: paraxial_approximation
    display_zh: 傍轴近似
    category: approximation
    aliases: ["近轴近似", "小倾角近似", "paraxial approximation"]
    description: 在光线接近光轴时线性化几何关系。

  - internal_id: small_angle_expansion
    display_zh: 小角展开
    category: approximation
    aliases: ["sinθ≈θ", "tanθ≈θ", "小角近似"]
    description: 对小角三角函数作低阶展开。

  - internal_id: first_order_expansion
    display_zh: 一阶展开
    category: approximation
    aliases: ["线性近似", "一阶微扰", "first-order expansion"]
    description: 保留小量一阶项简化方程。

  - internal_id: second_order_expansion
    display_zh: 二阶展开
    category: approximation
    aliases: ["二阶近似", "quadratic expansion", "保留二阶项"]
    description: 保留二阶小量分析稳定性或宽度。

  - internal_id: ray_differential_equation
    display_zh: 光线微分方程
    category: math_technique
    aliases: ["光线方程", "ray equation", "轨迹微分方程"]
    description: 由折射率函数建立光线路径方程。

  - internal_id: turning_point_condition
    display_zh: 转向点条件
    category: math_technique
    aliases: ["径向速度为零", "边界点条件", "turning point"]
    description: 用径向分量为零确定运动范围边界。

  - internal_id: conic_section_geometry
    display_zh: 圆锥曲线几何
    category: math_technique
    aliases: ["椭圆双曲线", "焦点性质", "conic sections"]
    description: 用圆锥曲线焦点性质处理严格成像。

  - internal_id: strict_stigmatic_imaging
    display_zh: 严格共轭成像
    category: physics_model
    aliases: ["严格成像", "等光程成像", "stigmatic imaging"]
    description: 要求物点到像点所有光路光程相等。

  - internal_id: spherical_refraction_imaging
    display_zh: 球面折射成像
    category: physics_law
    aliases: ["单球面折射", "球面界面成像", "spherical refraction"]
    description: 用球面界面公式求物像位置。

  - internal_id: spherical_mirror_imaging
    display_zh: 球面反射成像
    category: physics_law
    aliases: ["曲面镜成像", "球面镜公式", "spherical mirror"]
    description: 用球面反射近轴公式确定像点。

  - internal_id: thin_lens_formula
    display_zh: 薄透镜公式
    category: physics_law
    aliases: ["高斯公式", "1/u+1/v", "lens formula"]
    description: 用薄透镜物像距关系求成像。

  - internal_id: lensmaker_formula
    display_zh: 磨镜者公式
    category: physics_law
    aliases: ["透镜制造公式", "Lensmaker公式", "焦距曲率公式"]
    description: 用曲率半径和折射率计算焦距。

  - internal_id: newton_imaging_formula
    display_zh: 牛顿成像公式
    category: physics_law
    aliases: ["xx'=ff'", "Newton公式", "焦点坐标公式"]
    description: 用相对焦点距离表达共轭成像。

  - internal_id: lateral_magnification
    display_zh: 横向放大率
    category: physics_law
    aliases: ["放大率", "倍率", "transverse magnification"]
    description: 联系物高像高与物像距关系。

  - internal_id: sign_convention_imaging
    display_zh: 成像符号规则
    category: heuristic
    aliases: ["实虚正负", "物像距符号", "sign convention"]
    description: 用统一符号处理实物虚物实像虚像。

  - internal_id: principal_planes
    display_zh: 主面
    category: physics_model
    aliases: ["主点", "principal plane", "H面"]
    description: 用等高共轭面描述厚光具组。

  - internal_id: ideal_optical_system
    display_zh: 理想光具组
    category: physics_model
    aliases: ["共轴光具组", "高斯光学系统", "ideal optical system"]
    description: 用焦点主面描述复杂光学系统。

  - internal_id: abcd_matrix
    display_zh: ABCD矩阵
    category: math_technique
    aliases: ["光线转移矩阵", "矩阵光学", "ray transfer matrix"]
    description: 用矩阵串联描述共轴光线传播。

  - internal_id: sequential_imaging
    display_zh: 逐次成像
    category: heuristic
    aliases: ["前像后物", "光具组迭代", "successive imaging"]
    description: 将多元件成像拆成连续单元计算。

  - internal_id: aperture_stop_analysis
    display_zh: 光阑分析
    category: heuristic
    aliases: ["孔径限制", "入瞳出瞳", "aperture stop"]
    description: 判断限制成像光束的有效孔径。

  - internal_id: radiance_etendue
    display_zh: 光通量守恒
    category: physics_law
    aliases: ["亮度守恒", "étendue", "光展量"]
    description: 用光展量或亮度守恒计算光能传输。

  - internal_id: stellar_magnitude
    display_zh: 视星等
    category: physics_model
    aliases: ["星等公式", "apparent magnitude", "亮度等级"]
    description: 用对数亮度尺度比较天体观测亮度。

  - internal_id: photon_momentum
    display_zh: 光子动量
    category: physics_law
    aliases: ["p=h/lambda", "辐射动量", "photon momentum"]
    description: 用光子动量变化计算光压力或反冲。

  - internal_id: radiation_pressure
    display_zh: 光压
    category: physics_law
    aliases: ["辐射压", "光压力", "radiation pressure"]
    description: 用光动量通量求受光物体受力。

  - internal_id: optical_tweezer
    display_zh: 光镊
    category: physics_model
    aliases: ["光学捕获", "optical trap", "Ashkin光镊"]
    description: 用光场动量交换解释微粒捕获。

  - internal_id: thermal_lens_effect
    display_zh: 热透镜效应
    category: physics_model
    aliases: ["热透镜", "光强调制折射率", "thermal lensing"]
    description: 光强导致折射率分布并产生透镜效应。

  - internal_id: schlieren_method
    display_zh: 纹影法
    category: physics_model
    aliases: ["纹影成像", "Schlieren", "密度梯度显示"]
    description: 用折射率梯度偏折光线显示流场。

  - internal_id: rainbow_model
    display_zh: 彩虹模型
    category: physics_model
    aliases: ["水滴彩虹", "rainbow optics", "k级虹"]
    description: 用水滴内折反射解释彩虹偏折角。

  - internal_id: young_interference
    display_zh: 杨氏干涉
    category: physics_model
    aliases: ["双缝干涉", "Young干涉", "two-slit interference"]
    description: 用双光束相干叠加形成明暗条纹。

  - internal_id: optical_path_difference
    display_zh: 光程差
    category: physics_law
    aliases: ["相位差", "OPD", "path difference"]
    description: 用光程差判断干涉增强或相消。

  - internal_id: equal_inclination_interference
    display_zh: 等倾干涉
    category: physics_model
    aliases: ["等倾条纹", "Haidinger条纹", "equal inclination"]
    description: 由相同倾角光束形成同心干涉条纹。

  - internal_id: equal_thickness_interference
    display_zh: 等厚干涉
    category: physics_model
    aliases: ["薄膜干涉", "Fizeau条纹", "equal thickness"]
    description: 由薄膜厚度变化产生空间条纹。

  - internal_id: thin_film_interference
    display_zh: 薄膜干涉
    category: physics_law
    aliases: ["膜层干涉", "多光束薄膜", "thin-film interference"]
    description: 用膜内反射光程差分析透反光强。

  - internal_id: phase_reversal_reflection
    display_zh: 反射相变
    category: physics_law
    aliases: ["半波损失", "π相变", "phase reversal"]
    description: 判断反射时是否出现π相位跃变。

  - internal_id: visibility_contrast
    display_zh: 条纹可见度
    category: physics_law
    aliases: ["衬比度", "反差", "visibility"]
    description: 用强度极值衡量干涉条纹清晰度。

  - internal_id: extended_source_coherence
    display_zh: 扩展光源相干
    category: physics_model
    aliases: ["空间相干性", "非相干扩展源", "extended source"]
    description: 分析有限光源尺寸对干涉可见度影响。

  - internal_id: localized_interference
    display_zh: 定域干涉
    category: physics_model
    aliases: ["定域条纹", "localized fringes", "扩展源干涉"]
    description: 条纹只在特定空间区域保持高可见度。

  - internal_id: evanescent_wave
    display_zh: 隐失波
    category: physics_law
    aliases: ["倏逝波", "evanescent wave", "全反射近场"]
    description: 全反射界面外侧指数衰减的电磁场。

  - internal_id: anti_reflection_coating
    display_zh: 增透膜
    category: physics_model
    aliases: ["减反膜", "AR coating", "抗反射膜"]
    description: 用薄膜相消干涉降低表面反射。

  - internal_id: beamsplitter_model
    display_zh: 半透半反镜
    category: physics_model
    aliases: ["分束镜", "beam splitter", "半反镜"]
    description: 分析透射反射振幅和相位关系。

  - internal_id: multiple_reflection_sum
    display_zh: 多次反射求和
    category: math_technique
    aliases: ["等比级数求和", "多光束叠加", "multiple reflection"]
    description: 将多次反射振幅写成级数求和。

  - internal_id: sagnac_effect
    display_zh: 萨格纳克效应
    category: physics_law
    aliases: ["Sagnac效应", "转动干涉", "光纤陀螺"]
    description: 旋转参考系中两束反向光产生相位差。

  - internal_id: fraunhofer_diffraction
    display_zh: 夫琅和费衍射
    category: physics_law
    aliases: ["远场衍射", "Fraunhofer", "傅里叶衍射"]
    description: 用远场近似分析孔径衍射图样。

  - internal_id: fresnel_diffraction
    display_zh: 菲涅尔衍射
    category: physics_law
    aliases: ["近场衍射", "Fresnel", "半波带法"]
    description: 用近场相位二次项分析衍射。

  - internal_id: diffraction_grating
    display_zh: 衍射光栅
    category: physics_model
    aliases: ["光栅方程", "grating", "多缝衍射"]
    description: 多周期孔径产生离散衍射级次。

  - internal_id: blazed_grating
    display_zh: 闪耀光栅
    category: physics_model
    aliases: ["blazed grating", "闪耀角", "反射式光栅"]
    description: 用刻槽倾角增强特定衍射级光强。

  - internal_id: grating_equation
    display_zh: 光栅方程
    category: physics_law
    aliases: ["d sin theta", "衍射级次公式", "grating equation"]
    description: 联系光栅常数、波长与衍射方向。

  - internal_id: single_slit_diffraction
    display_zh: 单缝衍射
    category: physics_model
    aliases: ["缝衍射", "sinc图样", "single-slit"]
    description: 有限缝宽导致中央主极大和旁瓣。

  - internal_id: circular_aperture_diffraction
    display_zh: 圆孔衍射
    category: physics_model
    aliases: ["圆孔夫琅和费", "circular aperture", "Airy diffraction"]
    description: 圆孔远场产生艾里斑强度分布。

  - internal_id: airy_disk
    display_zh: 艾里斑
    category: physics_model
    aliases: ["Airy斑", "衍射极限光斑", "Airy disk"]
    description: 圆孔成像的中心衍射亮斑。

  - internal_id: rayleigh_criterion
    display_zh: 瑞利判据
    category: physics_law
    aliases: ["分辨本领", "Rayleigh criterion", "角分辨率"]
    description: 用艾里斑重叠条件判断可分辨性。

  - internal_id: fourier_transform_optics
    display_zh: 傅里叶光学
    category: math_technique
    aliases: ["孔径傅里叶变换", "频谱面", "Fourier optics"]
    description: 用孔径函数傅里叶变换求远场分布。

  - internal_id: convolution_theorem
    display_zh: 卷积定理
    category: math_technique
    aliases: ["傅里叶卷积", "convolution theorem", "频域乘积"]
    description: 用卷积与乘积关系处理复合孔径。

  - internal_id: fractal_diffraction
    display_zh: 分形衍射
    category: physics_model
    aliases: ["康托尔地毯", "fractal diffraction", "自相似衍射"]
    description: 自相似孔径产生递归结构衍射图样。

  - internal_id: huygens_fresnel_principle
    display_zh: 惠更斯原理
    category: physics_law
    aliases: ["惠更斯-菲涅尔", "Huygens-Fresnel", "次波源"]
    description: 将波前各点视为次级波源叠加。

  - internal_id: zone_plate_method
    display_zh: 半波带法
    category: heuristic
    aliases: ["菲涅尔波带", "zone method", "波带分析"]
    description: 用相邻半波带贡献估计衍射强度。

  - internal_id: scalar_diffraction_approx
    display_zh: 标量衍射近似
    category: approximation
    aliases: ["标量波近似", "忽略偏振", "scalar diffraction"]
    description: 忽略矢量电磁细节处理衍射问题。

  - internal_id: polarization_state
    display_zh: 偏振态
    category: physics_model
    aliases: ["线圆椭偏", "polarization state", "Jones态"]
    description: 描述光波电场振动方向和相位关系。

  - internal_id: malus_law
    display_zh: 马吕斯定律
    category: physics_law
    aliases: ["Malus law", "余弦平方定律", "偏振片透光"]
    description: 线偏振光经偏振片强度服从余弦平方。

  - internal_id: jones_calculus
    display_zh: 琼斯矩阵
    category: math_technique
    aliases: ["Jones矩阵", "偏振矩阵", "Jones calculus"]
    description: 用复振幅向量和矩阵计算偏振变化。

  - internal_id: birefringence
    display_zh: 双折射
    category: physics_law
    aliases: ["各向异性折射", "birefringence", "寻常非常光"]
    description: 各向异性介质中不同偏振折射率不同。

  - internal_id: wave_plate
    display_zh: 波片
    category: physics_model
    aliases: ["相位延迟片", "半波片", "四分之一波片"]
    description: 通过双折射相位延迟改变偏振态。

  - internal_id: brewster_angle
    display_zh: 布儒斯特角
    category: physics_law
    aliases: ["起偏角", "Brewster angle", "全偏振角"]
    description: 反射光某偏振分量消失的入射角。

  - internal_id: fresnel_equations
    display_zh: 菲涅尔公式
    category: physics_law
    aliases: ["Fresnel equations", "反射透射系数", "振幅系数"]
    description: 计算界面反射透射振幅和能流比例。

  - internal_id: polarization_interference
    display_zh: 偏振干涉
    category: physics_model
    aliases: ["正交偏振干涉", "polarization interference", "偏振光干涉"]
    description: 通过偏振投影使不同偏振分量相干叠加。

  - internal_id: electro_optic_effect
    display_zh: 电光效应
    category: physics_model
    aliases: ["人工双折射", "Kerr效应", "Pockels效应"]
    description: 外电场改变介质折射率或双折射。

  - internal_id: kerr_effect
    display_zh: 克尔效应
    category: physics_model
    aliases: ["二次电光效应", "Kerr effect", "电致双折射"]
    description: 折射率变化与外电场平方相关。

  - internal_id: pockels_effect
    display_zh: 泡克耳斯效应
    category: physics_model
    aliases: ["线性电光效应", "Pockels effect", "一次电光效应"]
    description: 折射率变化与外电场一次相关。

  - internal_id: rayleigh_scattering
    display_zh: 瑞利散射
    category: physics_law
    aliases: ["Rayleigh scattering", "蓝天散射", "短波强散射"]
    description: 小粒子散射强度随波长强烈变化。

  - internal_id: dipole_radiation
    display_zh: 电偶极辐射
    category: physics_model
    aliases: ["偶极子散射", "dipole radiation", "振荡电偶极"]
    description: 用受迫振荡电偶极解释散射角分布。

  - internal_id: dispersion_relation
    display_zh: 色散关系
    category: physics_law
    aliases: ["频率波矢关系", "dispersion relation", "omega-k关系"]
    description: 描述波频率与波矢之间的函数关系。

  - internal_id: group_velocity
    display_zh: 群速度
    category: physics_law
    aliases: ["波包速度", "group velocity", "dω/dk"]
    description: 用色散关系导数确定波包传播速度。

  - internal_id: phase_velocity
    display_zh: 相速度
    category: physics_law
    aliases: ["波峰速度", "phase velocity", "ω/k"]
    description: 描述单色相位面传播速度。

  - internal_id: photon_gas
    display_zh: 光子气体
    category: physics_model
    aliases: ["二维光子气体", "photon gas", "黑体光子"]
    description: 将光子集合视为满足统计规律的气体。

  - internal_id: de_broglie_wavelength
    display_zh: 德布罗意波长
    category: physics_law
    aliases: ["物质波长", "de Broglie wavelength", "λ=h/p"]
    description: 用动量确定微观粒子的物质波长。

  - internal_id: bose_einstein_condensation
    display_zh: 玻色凝聚
    category: physics_model
    aliases: ["BEC", "玻色-爱因斯坦凝聚", "Bose-Einstein condensation"]
    description: 玻色粒子在低温下宏观占据基态。

  - internal_id: quantum_tunneling
    display_zh: 量子隧穿
    category: physics_law
    aliases: ["隧穿效应", "tunneling", "势垒穿透"]
    description: 波函数可穿过经典禁止区域。

  - internal_id: uncertainty_relation
    display_zh: 不确定关系
    category: physics_law
    aliases: ["测不准关系", "Heisenberg uncertainty", "ΔxΔp"]
    description: 不对易物理量不能同时任意精确确定。

  - internal_id: perturbation_theory
    display_zh: 微扰理论
    category: math_technique
    aliases: ["量子微扰", "perturbation theory", "小扰动修正"]
    description: 用小扰动展开求能级或状态修正。

  - internal_id: bohr_quantization
    display_zh: 玻尔量子化
    category: physics_law
    aliases: ["角动量量子化", "Bohr condition", "nħ"]
    description: 用角动量或驻波条件离散化轨道。

  - internal_id: hydrogen_like_model
    display_zh: 类氢模型
    category: physics_model
    aliases: ["类氢原子", "Bohr模型", "hydrogen-like model"]
    description: 用中心势和量子化条件描述束缚体系。

  - internal_id: relativistic_correction
    display_zh: 相对论修正
    category: approximation
    aliases: ["狭义相对论修正", "relativistic correction", "高速修正"]
    description: 在高速粒子问题中修正经典动能关系。

  - internal_id: resonance_condition
    display_zh: 共振条件
    category: physics_law
    aliases: ["resonance", "驻波条件", "本征频率匹配"]
    description: 当外界或边界条件匹配本征频率时增强响应。

  - internal_id: harmonic_stability_analysis
    display_zh: 简谐稳定性
    category: math_technique
    aliases: ["小振动分析", "稳定轨道判据", "linear stability"]
    description: 对平衡轨道附近扰动作线性稳定分析。
version: "v0.1"
tags:
  - internal_id: boltzmann_distribution
    display_zh: 玻尔兹曼分布
    category: physics_law
    aliases: ["Boltzmann分布", "指数分布"]
    description: 用能量指数权重描述热平衡态概率分布。

  - internal_id: maxwell_velocity_distribution
    display_zh: 麦克斯韦分布
    category: physics_law
    aliases: ["Maxwell分布", "速度分布律"]
    description: 描述理想气体分子速度分量和速率分布。

  - internal_id: equipartition_theorem
    display_zh: 能均分定理
    category: physics_law
    aliases: ["能量均分", "equipartition"]
    description: 每个二次型自由度平均贡献相同热能。

  - internal_id: ideal_gas_equation
    display_zh: 理想气体方程
    category: physics_law
    aliases: ["PV=nRT", "状态方程"]
    description: 联系理想气体压强、体积、温度和物质的量。

  - internal_id: first_law_thermodynamics
    display_zh: 热力学第一定律
    category: physics_law
    aliases: ["能量守恒", "dQ=dU+dW"]
    description: 用内能变化、吸热和做功建立能量账本。

  - internal_id: carnot_efficiency
    display_zh: 卡诺效率
    category: physics_law
    aliases: ["Carnot效率", "可逆热机效率"]
    description: 给出两热源间可逆热机的极限效率。

  - internal_id: clausius_entropy
    display_zh: 克劳修斯熵
    category: physics_law
    aliases: ["Clausius熵", "dS=dQ/T"]
    description: 通过可逆热量积分定义宏观熵变。

  - internal_id: boltzmann_entropy
    display_zh: 玻尔兹曼熵
    category: physics_law
    aliases: ["S=klnW", "微观态熵"]
    description: 用微观态数刻画热力学熵。

  - internal_id: gibbs_mixing_entropy
    display_zh: 混合熵
    category: physics_law
    aliases: ["Gibbs熵", "气体混合熵"]
    description: 描述不同气体混合导致的熵增加。

  - internal_id: maxwell_relation
    display_zh: 麦克斯韦关系
    category: physics_law
    aliases: ["热力学关系", "Maxwell关系"]
    description: 由热力学势的全微分导出偏导关系。

  - internal_id: fourier_heat_conduction
    display_zh: 傅里叶定律
    category: physics_law
    aliases: ["Fourier定律", "热传导定律"]
    description: 热流密度与温度梯度成正比。

  - internal_id: newton_cooling_law
    display_zh: 牛顿冷却
    category: physics_law
    aliases: ["对流换热", "Newton冷却"]
    description: 描述物体与环境间的线性对流换热。

  - internal_id: stefan_boltzmann_law
    display_zh: 斯特藩定律
    category: physics_law
    aliases: ["Stefan-Boltzmann", "黑体辐射定律"]
    description: 黑体辐射功率与热力学温度四次方成正比。

  - internal_id: radiation_pressure
    display_zh: 辐射压
    category: physics_law
    aliases: ["光压", "radiation pressure"]
    description: 电磁辐射携带动量并对物体产生压强。

  - internal_id: photon_gas_equation
    display_zh: 光子气方程
    category: physics_law
    aliases: ["光子气压强", "p=u/3"]
    description: 用能量密度关系描述光子气压强。

  - internal_id: laplace_pressure
    display_zh: 拉普拉斯压强
    category: physics_law
    aliases: ["Laplace压强", "曲面压强差"]
    description: 表面张力导致曲面内外出现压强差。

  - internal_id: surface_tension_balance
    display_zh: 表面张力平衡
    category: physics_law
    aliases: ["液面张力", "界面张力"]
    description: 用界面张力与外力建立液体表面平衡。

  - internal_id: capillary_rise
    display_zh: 毛细现象
    category: physics_law
    aliases: ["毛细上升", "毛细管效应"]
    description: 表面张力与液柱重力共同决定液面高度。

  - internal_id: clapeyron_equation
    display_zh: 克拉珀龙方程
    category: physics_law
    aliases: ["Clapeyron方程", "相变曲线方程"]
    description: 联系相变潜热与相平衡曲线斜率。

  - internal_id: latent_heat_relation
    display_zh: 潜热关系
    category: physics_law
    aliases: ["相变潜热", "汽化热"]
    description: 描述物态变化过程中吸放热与质量关系。

  - internal_id: saturated_vapor_pressure
    display_zh: 饱和蒸气压
    category: physics_law
    aliases: ["饱和汽压", "蒸气压"]
    description: 描述液汽平衡时蒸气压随温度变化。

  - internal_id: thermal_expansion_law
    display_zh: 热膨胀规律
    category: physics_law
    aliases: ["线膨胀", "体膨胀"]
    description: 描述物体尺寸随温度变化的线性近似关系。

  - internal_id: virial_theorem
    display_zh: 维里定理
    category: physics_law
    aliases: ["位力定理", "virial theorem"]
    description: 联系束缚体系平均动能与势能。

  - internal_id: fluid_hydrostatic_equilibrium
    display_zh: 流体静平衡
    category: physics_law
    aliases: ["静力平衡", "压强梯度平衡"]
    description: 用压强梯度平衡体力或引力作用。

  - internal_id: brownian_diffusion
    display_zh: 布朗扩散
    category: physics_law
    aliases: ["扩散方程", "随机游走扩散"]
    description: 用随机运动导致的均方位移描述扩散。

  - internal_id: einstein_relation
    display_zh: 爱因斯坦关系
    category: physics_law
    aliases: ["迁移率扩散关系", "Einstein关系"]
    description: 联系扩散系数、迁移率与温度。

  - internal_id: displacement_polarization
    display_zh: 位移极化
    category: physics_model
    aliases: ["诱导极化", "电子位移极化"]
    description: 用束缚电荷相对位移建立介质极化模型。

  - internal_id: orientational_polarization
    display_zh: 取向极化
    category: physics_model
    aliases: ["偶极取向", "极性分子极化"]
    description: 用偶极矩在外场中的统计取向描述极化。

  - internal_id: debye_relaxation
    display_zh: 德拜弛豫
    category: physics_model
    aliases: ["Debye驰豫", "极化弛豫"]
    description: 描述交变场中偶极取向滞后和损耗。

  - internal_id: lorentz_oscillator
    display_zh: 洛伦兹振子
    category: physics_model
    aliases: ["束缚电子振子", "Lorentz模型"]
    description: 用受迫振动电子模型解释介质色散。

  - internal_id: einstein_solid
    display_zh: 爱因斯坦固体
    category: physics_model
    aliases: ["Einstein热容模型", "量子谐振子固体"]
    description: 把固体原子视为独立量子谐振子。

  - internal_id: gas_spring_model
    display_zh: 气体弹簧
    category: physics_model
    aliases: ["气弹簧", "气体回复力"]
    description: 用气体压强变化产生等效弹性回复力。

  - internal_id: piston_gas_model
    display_zh: 活塞气体
    category: physics_model
    aliases: ["活塞模型", "气缸模型"]
    description: 用活塞位置约束两侧气体状态变化。

  - internal_id: rotating_cylinder_gas
    display_zh: 旋转气缸
    category: physics_model
    aliases: ["转动气缸", "环形气缸"]
    description: 结合旋转运动、活塞约束与气体准静态过程。

  - internal_id: polarized_gas_capacitor
    display_zh: 极化气体
    category: physics_model
    aliases: ["介质气体", "电场极化气体"]
    description: 将气体分子极化能并入统计平衡分布。

  - internal_id: self_gravitating_gas
    display_zh: 自引力气体
    category: physics_model
    aliases: ["气态星球", "引力气体球"]
    description: 描述气体在自身引力和热压强下的平衡。

  - internal_id: jeans_instability
    display_zh: 金斯判据
    category: physics_model
    aliases: ["Jeans判据", "恒星形成判据"]
    description: 判断气体云能否在引力下塌缩成星。

  - internal_id: photon_gas_model
    display_zh: 光子气模型
    category: physics_model
    aliases: ["辐射气体", "黑体腔模型"]
    description: 把热辐射视作满足统计规律的光子体系。

  - internal_id: blackbody_cavity
    display_zh: 黑体腔
    category: physics_model
    aliases: ["空腔辐射", "黑体辐射腔"]
    description: 用封闭空腔模型处理平衡热辐射。

  - internal_id: soap_film_model
    display_zh: 泡膜模型
    category: physics_model
    aliases: ["肥皂膜", "液膜振动"]
    description: 用双液面表面张力分析薄膜平衡与振动。

  - internal_id: capillary_column_model
    display_zh: 毛细管液柱
    category: physics_model
    aliases: ["液柱模型", "毛细管模型"]
    description: 用液柱重力与曲面压强差分析毛细现象。

  - internal_id: heat_conduction_rod
    display_zh: 导热细杆
    category: physics_model
    aliases: ["热传导杆", "一维导热杆"]
    description: 将温度场简化为一维杆上的热传导问题。

  - internal_id: spherical_star_model
    display_zh: 球形恒星
    category: physics_model
    aliases: ["恒星结构", "球对称星体"]
    description: 用球对称平衡方程分析恒星内部结构。

  - internal_id: kinetic_transport_model
    display_zh: 输运模型
    category: physics_model
    aliases: ["分子输运", "平均自由程模型"]
    description: 从分子碰撞和自由程估算热量或动量输运。

  - internal_id: quasi_static_process
    display_zh: 准静态过程
    category: heuristic
    aliases: ["缓慢过程", "平衡态路径"]
    description: 把过程分解为连续平衡态以使用状态方程。

  - internal_id: energy_accounting
    display_zh: 能量账本
    category: heuristic
    aliases: ["能量清算", "热功内能分解"]
    description: 系统区分内能、做功、热量和势能贡献。

  - internal_id: entropy_accounting
    display_zh: 熵变账本
    category: heuristic
    aliases: ["熵清算", "熵产生分析"]
    description: 分别计算系统、环境和总熵变化。

  - internal_id: micro_to_macro_average
    display_zh: 微宏平均
    category: heuristic
    aliases: ["统计平均", "微观到宏观"]
    description: 通过微观分布平均得到宏观物理量。

  - internal_id: flux_balance
    display_zh: 通量平衡
    category: heuristic
    aliases: ["流量守恒", "通量差分"]
    description: 用进入与流出通量差建立局域变化方程。

  - internal_id: steady_state_balance
    display_zh: 稳态平衡
    category: heuristic
    aliases: ["定常平衡", "稳恒条件"]
    description: 在时间不变条件下令净流量或净功率为零。

  - internal_id: symmetry_reduction
    display_zh: 对称降维
    category: heuristic
    aliases: ["球对称化", "柱对称化"]
    description: 利用几何对称性减少变量和方程维数。

  - internal_id: trial_solution_ansatz
    display_zh: 试探解
    category: heuristic
    aliases: ["ansatz", "猜解"]
    description: 代入特定函数形式简化难解微分方程。

  - internal_id: phase_diagram_reading
    display_zh: 相图判断
    category: heuristic
    aliases: ["相变图像", "相平衡图"]
    description: 用相图确定相态、相变方向和临界条件。

  - internal_id: effective_spring
    display_zh: 等效弹簧
    category: heuristic
    aliases: ["等效回复力", "有效劲度系数"]
    description: 将压强或表面张力效应转化为线性回复力。

  - internal_id: small_element_balance
    display_zh: 微元平衡
    category: heuristic
    aliases: ["微元受力", "微元守恒"]
    description: 对微小体元列平衡或守恒方程。

  - internal_id: limiting_case_check
    display_zh: 极限检验
    category: heuristic
    aliases: ["高低温极限", "边界检验"]
    description: 用特殊极限检查结果合理性和物理意义。

  - internal_id: gaussian_integral
    display_zh: 高斯积分
    category: math_technique
    aliases: ["正态积分", "Gaussian integral"]
    description: 计算含二次指数分布的归一化和矩。

  - internal_id: gamma_function_integral
    display_zh: 伽马积分
    category: math_technique
    aliases: ["Gamma函数", "Γ函数"]
    description: 处理幂函数乘指数函数的定积分。

  - internal_id: probability_normalization
    display_zh: 概率归一化
    category: math_technique
    aliases: ["归一化常数", "normalization"]
    description: 通过总概率为一确定分布函数系数。

  - internal_id: coordinate_transform
    display_zh: 坐标变换
    category: math_technique
    aliases: ["变量替换", "换元"]
    description: 通过合适坐标或变量替换简化积分。

  - internal_id: spherical_integration
    display_zh: 球坐标积分
    category: math_technique
    aliases: ["立体角积分", "角向积分"]
    description: 用球坐标和立体角处理取向或球对称问题。

  - internal_id: cylindrical_integration
    display_zh: 柱坐标积分
    category: math_technique
    aliases: ["圆柱坐标", "径向积分"]
    description: 用柱坐标处理圆筒、电场和导热问题。

  - internal_id: series_expansion
    display_zh: 级数展开
    category: math_technique
    aliases: ["泰勒展开", "Taylor展开"]
    description: 对小参数函数展开并保留主导项。

  - internal_id: differential_equation
    display_zh: 微分方程
    category: math_technique
    aliases: ["ODE", "PDE"]
    description: 通过连续变量方程描述系统演化或平衡。

  - internal_id: separation_of_variables
    display_zh: 分离变量
    category: math_technique
    aliases: ["变量分离", "separation"]
    description: 将偏微分方程拆成空间和时间方程求解。

  - internal_id: integrating_factor
    display_zh: 积分因子
    category: math_technique
    aliases: ["全微分因子", "integrating factor"]
    description: 将一阶微分方程化为可直接积分形式。

  - internal_id: eigenmode_expansion
    display_zh: 本征模展开
    category: math_technique
    aliases: ["模态展开", "Fourier展开"]
    description: 用边界条件下的本征函数展开温度或振动场。

  - internal_id: complex_amplitude_method
    display_zh: 复振幅法
    category: math_technique
    aliases: ["相量法", "复数表示"]
    description: 用复指数处理简谐驱动和相位差问题。

  - internal_id: damped_oscillator_solution
    display_zh: 阻尼振子求解
    category: math_technique
    aliases: ["受迫振动", "阻尼振动"]
    description: 求解含阻尼、回复力和外驱动的线性振子。

  - internal_id: dimensional_analysis
    display_zh: 量纲分析
    category: math_technique
    aliases: ["量纲检验", "scaling"]
    description: 用量纲关系约束公式形式和物理尺度。

  - internal_id: asymptotic_matching
    display_zh: 渐近估计
    category: math_technique
    aliases: ["数量级估计", "asymptotic"]
    description: 在参数极限下保留主导量并估计结果。

  - internal_id: small_angle_linearization
    display_zh: 小角线性化
    category: approximation
    aliases: ["sinθ≈θ", "小角近似"]
    description: 将角函数在小角范围内化为线性形式。

  - internal_id: high_temperature_limit
    display_zh: 高温极限
    category: approximation
    aliases: ["kT远大", "经典极限"]
    description: 在热能远大于特征能量时展开物理量。

  - internal_id: low_temperature_limit
    display_zh: 低温极限
    category: approximation
    aliases: ["低温近似", "指数抑制"]
    description: 在热能远小于特征能量时保留最低激发贡献。

  - internal_id: weak_field_expansion
    display_zh: 弱场展开
    category: approximation
    aliases: ["高温弱场", "小电场展开"]
    description: 对外场能量远小于热能的情形作线性展开。

  - internal_id: thin_shell_approximation
    display_zh: 薄层近似
    category: approximation
    aliases: ["薄板近似", "薄壳近似"]
    description: 忽略厚度高阶影响并按薄层积分处理。

  - internal_id: continuum_approximation
    display_zh: 连续介质近似
    category: approximation
    aliases: ["连续化", "连续场近似"]
    description: 将离散粒子体系近似为连续密度场。

  - internal_id: dilute_gas_approximation
    display_zh: 稀薄气体近似
    category: approximation
    aliases: ["理想稀薄气体", "低密度近似"]
    description: 忽略分子间相互作用并保留碰撞统计效应。

  - internal_id: mean_free_path_approximation
    display_zh: 平均自由程近似
    category: approximation
    aliases: ["自由程估计", "λ近似"]
    description: 用平均自由程估算输运系数和热流。

  - internal_id: steady_state_approximation
    display_zh: 稳态近似
    category: approximation
    aliases: ["定常近似", "时间项忽略"]
    description: 忽略时间变化项以求稳定分布。

  - internal_id: quasistatic_approximation
    display_zh: 准静态近似
    category: approximation
    aliases: ["慢变近似", "平衡近似"]
    description: 认为过程足够慢以持续满足平衡关系。

  - internal_id: linear_response
    display_zh: 线性响应
    category: approximation
    aliases: ["一阶响应", "linear response"]
    description: 只保留外界扰动的一阶物理响应。

  - internal_id: far_field_approximation
    display_zh: 远场近似
    category: approximation
    aliases: ["辐射远区", "远区近似"]
    description: 在距离远大于源尺度时简化辐射场表达式。

  - internal_id: lumped_capacity_approximation
    display_zh: 集总热容近似
    category: approximation
    aliases: ["集总参数", "均温近似"]
    description: 将物体内部温度视作空间均匀变量。

  - internal_id: negligible_radiation_loss
    display_zh: 忽略辐射损失
    category: approximation
    aliases: ["无辐射损失", "辐射忽略"]
    description: 在传导或对流主导时忽略热辐射项。

version: "v0.1"
tags:
  - internal_id: lorentz_transformation_vector
    display_zh: 矢量洛伦兹变换
    category: physics_law
    aliases: ["洛伦兹变换矢量式", "vector Lorentz transform"]
    description: 用平行与垂直分量统一处理任意方向换系。

  - internal_id: relativity_of_simultaneity
    display_zh: 同时相对性
    category: physics_law
    aliases: ["不同系不同同时", "simultaneity relativity"]
    description: 判断不同参考系中事件同时性的改变。

  - internal_id: directional_length_contraction
    display_zh: 方向性尺缩
    category: physics_law
    aliases: ["沿运动方向收缩", "length contraction"]
    description: 只对速度方向上的长度进行洛伦兹收缩。

  - internal_id: proper_length_identification
    display_zh: 本征长度识别
    category: heuristic
    aliases: ["静长判断", "proper length"]
    description: 先判断哪一参考系中物体长度是本征长度。

  - internal_id: velocity_addition_collinear
    display_zh: 共线速度合成
    category: physics_law
    aliases: ["相对论速度叠加", "collinear velocity addition"]
    description: 用相对论速度加法处理同向或反向运动。

  - internal_id: velocity_addition_vector
    display_zh: 矢量速度合成
    category: physics_law
    aliases: ["非共线速度合成", "vector velocity addition"]
    description: 分解平行垂直分量处理非共线速度变换。

  - internal_id: relativistic_acceleration_transform
    display_zh: 加速度变换
    category: physics_law
    aliases: ["相对论加速度变换", "acceleration transform"]
    description: 在不同惯性系间转换粒子加速度与时间关系。

  - internal_id: proper_time_clock_reading
    display_zh: 本征时读数
    category: physics_law
    aliases: ["固有时", "proper time"]
    description: 用运动物体自身钟的固有时表示过程时间。

  - internal_id: spacetime_event_matching
    display_zh: 时空事件配对
    category: heuristic
    aliases: ["事件法", "event matching"]
    description: 将发射、接收、碰撞等过程拆成时空事件求解。

  - internal_id: light_cone_intersection
    display_zh: 光锥交点法
    category: heuristic
    aliases: ["光信号交会", "light cone intersection"]
    description: 用光速传播条件确定信号发射接收事件。

  - internal_id: retarded_time_geometry
    display_zh: 推迟时几何
    category: heuristic
    aliases: ["视位置延迟", "retarded time"]
    description: 由光传播时间反推观察到的物体表观形状。

  - internal_id: relativistic_visual_shape
    display_zh: 相对论视形
    category: physics_model
    aliases: ["视觉畸变", "Terrell effect"]
    description: 分析高速运动物体因光时延产生的表观形状。

  - internal_id: relativistic_center_of_momentum
    display_zh: 相对论质心系
    category: heuristic
    aliases: ["零动量系", "COM frame"]
    description: 转到总动量为零的参考系简化碰撞或爆炸。

  - internal_id: invariant_mass_method
    display_zh: 不变质量法
    category: heuristic
    aliases: ["不变量法", "invariant mass"]
    description: 用四动量平方不变量求阈能或反应结果。

  - internal_id: energy_momentum_relation
    display_zh: 能动关系
    category: physics_law
    aliases: ["相对论能量动量", "E-p relation"]
    description: 用能量动量关系连接质量、动量和总能量。

  - internal_id: relativistic_threshold_energy
    display_zh: 阈能条件
    category: physics_law
    aliases: ["反应阈值", "threshold energy"]
    description: 由末态质心系静止条件确定反应最低能量。

  - internal_id: pair_annihilation_kinematics
    display_zh: 湮灭运动学
    category: physics_model
    aliases: ["正负电子湮灭", "annihilation kinematics"]
    description: 用能动守恒处理粒子反粒子转化为光子。

  - internal_id: photon_aberration
    display_zh: 光行差公式
    category: physics_law
    aliases: ["相对论光行差", "aberration"]
    description: 描述光子方向在不同惯性系中的角度变换。

  - internal_id: massive_particle_aberration
    display_zh: 有质量粒子行差
    category: physics_law
    aliases: ["粒子角变换", "massive aberration"]
    description: 描述中微子等有质量粒子速度方向的换系。

  - internal_id: relativistic_beaming
    display_zh: 相对论束射
    category: physics_model
    aliases: ["前向聚束", "relativistic beaming"]
    description: 高速源的辐射在观察系中向前方集中。

  - internal_id: wigner_rotation
    display_zh: 魏格纳转动
    category: physics_law
    aliases: ["Wigner rotation", "非共线boost转动"]
    description: 两次非共线洛伦兹变换导致参考系空间转动。

  - internal_id: thomas_precession
    display_zh: 托马斯进动
    category: physics_law
    aliases: ["Thomas precession", "托马斯旋进"]
    description: 加速粒子瞬时共动系连续变化产生附加进动。

  - internal_id: low_velocity_beta_expansion
    display_zh: 低速β展开
    category: approximation
    aliases: ["保留β二阶", "low beta expansion"]
    description: 在速度远小于光速时按β阶数展开相对论效应。

  - internal_id: weak_field_light_deflection
    display_zh: 弱场光偏折
    category: physics_model
    aliases: ["引力光线偏折", "light bending"]
    description: 计算太阳附近光线在引力场中的偏转角。

  - internal_id: gravitational_impulse_method
    display_zh: 引力冲量法
    category: heuristic
    aliases: ["横向冲量", "impulse method"]
    description: 将微弱偏折近似为沿直线路径累积横向冲量。

  - internal_id: orbit_equation_perturbation
    display_zh: 轨道方程微扰
    category: math_technique
    aliases: ["u=1/r微扰", "orbit perturbation"]
    description: 用倒半径轨道方程和小修正求偏折或进动。

  - internal_id: effective_potential_orbit
    display_zh: 有效势轨道
    category: heuristic
    aliases: ["径向有效势", "effective potential"]
    description: 将中心力运动化为一维径向有效势问题。

  - internal_id: geodesic_weak_field
    display_zh: 弱场测地线
    category: physics_model
    aliases: ["Schwarzschild弱场", "weak-field geodesic"]
    description: 用弱引力度规中的测地线计算轨道修正。

  - internal_id: photon_rocket_equation
    display_zh: 光子火箭方程
    category: physics_model
    aliases: ["相对论火箭", "photon rocket"]
    description: 用光子动量排放建立质量比与速度关系。

  - internal_id: relativistic_radiation_damping
    display_zh: 相对论辐射阻尼
    category: physics_model
    aliases: ["辐射耗散", "radiation damping"]
    description: 处理带电振子因电磁辐射损失能量的衰减。

  - internal_id: poynting_robertson_drag
    display_zh: 坡印廷罗伯逊阻力
    category: physics_model
    aliases: ["P-R阻力", "Poynting-Robertson effect"]
    description: 运动尘埃吸收再辐射导致切向辐射阻力。

  - internal_id: relativistic_cyclotron_frequency
    display_zh: 相对论回旋频率
    category: physics_law
    aliases: ["回旋频率降低", "relativistic cyclotron"]
    description: 粒子能量升高导致回旋频率随γ因子改变。

  - internal_id: cherenkov_condition
    display_zh: 切伦科夫条件
    category: physics_law
    aliases: ["切连科夫辐射", "Cherenkov condition"]
    description: 粒子速度超过介质光速时产生锥形辐射。

  - internal_id: photodisintegration_threshold
    display_zh: 光致裂变阈值
    category: physics_model
    aliases: ["光核反应阈能", "photodisintegration"]
    description: 用能量动量守恒求光子击出核子阈能。

  - internal_id: electromagnetic_field_transform
    display_zh: 电磁场变换
    category: physics_law
    aliases: ["E-B变换", "field transform"]
    description: 在不同惯性系间变换电场和磁场分量。

  - internal_id: four_current_transform
    display_zh: 四维电流变换
    category: physics_law
    aliases: ["电荷电流四矢量", "four-current"]
    description: 将电荷密度和电流密度作为四矢量变换。

  - internal_id: relativistic_lorentz_force
    display_zh: 相对论洛伦兹力
    category: physics_law
    aliases: ["电磁力运动", "relativistic Lorentz force"]
    description: 结合相对论动量方程处理带电粒子运动。

  - internal_id: energy_momentum_integral
    display_zh: 能动积分法
    category: heuristic
    aliases: ["积分方程联立", "energy-momentum integral"]
    description: 用能量方程与动量方程积分求相对论运动。

  - internal_id: radiation_pressure_mirror
    display_zh: 镜面光压
    category: physics_law
    aliases: ["反射光压", "radiation pressure"]
    description: 用光子动量变化计算镜面受到的推力。

  - internal_id: relativistic_solar_sail
    display_zh: 相对论太阳帆
    category: physics_model
    aliases: ["光帆模型", "solar sail"]
    description: 考虑速度效应下光压持续推动飞船加速。

  - internal_id: rutherford_scattering
    display_zh: 卢瑟福散射
    category: physics_model
    aliases: ["α粒子散射", "Rutherford scattering"]
    description: 用点核库仑斥力解释大角度α粒子散射。

  - internal_id: thomson_plum_pudding_model
    display_zh: 西瓜模型
    category: physics_model
    aliases: ["汤姆孙模型", "plum pudding model"]
    description: 将正电荷视作均匀分布球体估算散射偏角。

  - internal_id: coulomb_scattering_angle
    display_zh: 库仑散射角
    category: physics_law
    aliases: ["双曲线散射", "Coulomb scattering"]
    description: 由库仑势和瞄准距离确定粒子偏转角。

  - internal_id: differential_cross_section
    display_zh: 微分截面
    category: physics_law
    aliases: ["散射截面", "differential cross section"]
    description: 用单位立体角散射粒子数表征散射概率。

  - internal_id: impact_parameter_mapping
    display_zh: 瞄准距映射
    category: heuristic
    aliases: ["b-θ关系", "impact parameter"]
    description: 建立瞄准距离和散射角之间的对应关系。

  - internal_id: lab_cm_angle_transform
    display_zh: 质心实验角变换
    category: math_technique
    aliases: ["CM-Lab角变换", "angle transform"]
    description: 将质心系散射角转换为实验室系观测角。

  - internal_id: central_potential_scattering
    display_zh: 中心势散射
    category: physics_model
    aliases: ["有心力散射", "central potential scattering"]
    description: 用中心势轨道求入射粒子的散射角和截面。

  - internal_id: inverse_square_potential_scattering
    display_zh: 平方反比势散射
    category: physics_model
    aliases: ["α/r²势散射", "inverse-square potential"]
    description: 处理势能正比于反平方距离的经典散射。

  - internal_id: square_well_scattering
    display_zh: 球形势阱散射
    category: physics_model
    aliases: ["有限深势阱", "spherical well scattering"]
    description: 用折射式轨迹处理球形有限势阱散射。

  - internal_id: scattering_refraction_analogy
    display_zh: 散射折射类比
    category: heuristic
    aliases: ["力学折射", "refraction analogy"]
    description: 将势阱中速度改变类比为光线折射求偏折。

  - internal_id: resonant_photon_recoil
    display_zh: 共振光子反冲
    category: physics_model
    aliases: ["光吸收反冲", "photon recoil"]
    description: 原子吸收发射共振光子后获得累计反冲动量。

  - internal_id: rapidity_parameterization
    display_zh: 快速度参数
    category: math_technique
    aliases: ["双曲角", "rapidity"]
    description: 用双曲函数参数化相对论速度和能量动量。

  - internal_id: doppler_resonance_condition
    display_zh: 多普勒共振条件
    category: physics_law
    aliases: ["频率调谐", "Doppler resonance"]
    description: 调整入射光频率使运动原子仍能共振吸收。

  - internal_id: compton_scattering
    display_zh: 康普顿散射
    category: physics_model
    aliases: ["光子电子散射", "Compton scattering"]
    description: 用相对论能动守恒处理光子与电子散射。

  - internal_id: klein_nishina_formula
    display_zh: 克莱因仁科公式
    category: physics_law
    aliases: ["Klein-Nishina", "康普顿截面"]
    description: 给出相对论光子电子散射的角分布截面。

  - internal_id: thomson_limit
    display_zh: 汤姆逊极限
    category: approximation
    aliases: ["低频极限", "Thomson limit"]
    description: 光子能量远小于电子静能时的散射近似。

  - internal_id: invariant_phase_space
    display_zh: 不变相空间
    category: math_technique
    aliases: ["Lorentz不变相空间", "invariant phase space"]
    description: 用洛伦兹不变相空间元计算二体散射截面。

  - internal_id: mandelstam_invariants
    display_zh: 曼德尔斯塔姆量
    category: math_technique
    aliases: ["s t u变量", "Mandelstam variables"]
    description: 用散射不变量化简相对论散射运动学。

  - internal_id: compton_edge_spectrum
    display_zh: 康普顿边
    category: physics_model
    aliases: ["康普顿电子谱", "Compton edge"]
    description: 由最大反冲电子能量解释能谱截止边缘。

  - internal_id: scintillator_response_model
    display_zh: 闪烁体响应
    category: physics_model
    aliases: ["闪烁探测", "scintillator response"]
    description: 将电子沉积能量转化为探测器电压脉冲。

  - internal_id: blackbody_exchange
    display_zh: 黑体辐射交换
    category: physics_model
    aliases: ["部分黑体传热", "radiative exchange"]
    description: 计算两个部分黑体之间的净辐射传热。

  - internal_id: view_factor_reciprocity
    display_zh: 角系数互易
    category: physics_law
    aliases: ["形态因子互易", "view factor reciprocity"]
    description: 用面积和吸收比例互易关系保证热平衡。

  - internal_id: lambertian_radiation
    display_zh: 朗伯辐射
    category: physics_model
    aliases: ["余弦辐射", "Lambertian"]
    description: 用余弦角分布描述漫射黑体表面辐射。

  - internal_id: larmor_radiation_loss
    display_zh: 拉莫尔辐射损失
    category: physics_law
    aliases: ["加速电荷辐射", "Larmor formula"]
    description: 用加速电荷辐射功率估算经典原子塌缩。

  - internal_id: bohr_quantization
    display_zh: 玻尔量子化
    category: physics_model
    aliases: ["角动量量子化", "Bohr model"]
    description: 用角动量量子化求氢原子能级和轨道半径。

  - internal_id: sommerfeld_quantization
    display_zh: 索末菲量子化
    category: physics_model
    aliases: ["作用量子化", "Sommerfeld quantization"]
    description: 对椭圆轨道的径向和角向作用量进行量子化。

  - internal_id: action_variable_integral
    display_zh: 作用量积分
    category: math_technique
    aliases: ["相积分", "action integral"]
    description: 计算闭合轨道上的广义动量积分量子化条件。

  - internal_id: relativistic_fine_structure
    display_zh: 相对论精细结构
    category: physics_model
    aliases: ["氢精细结构", "fine structure"]
    description: 用相对论修正解释氢原子谱线精细劈裂。

  - internal_id: wkb_quantization
    display_zh: WKB量子化
    category: approximation
    aliases: ["半经典量子化", "WKB"]
    description: 用半经典相积分条件近似求束缚态能级。

  - internal_id: langer_correction
    display_zh: 兰格修正
    category: approximation
    aliases: ["l+1/2修正", "Langer correction"]
    description: 中心势径向WKB中将角动量量子数作半整数修正。

  - internal_id: spin_orbit_coupling
    display_zh: 自旋轨道耦合
    category: physics_law
    aliases: ["LS耦合", "spin-orbit coupling"]
    description: 电子自旋磁矩与轨道磁场相互作用导致能级劈裂。

  - internal_id: thomas_half_factor
    display_zh: 托马斯半因子
    category: approximation
    aliases: ["1/2因子", "Thomas factor"]
    description: 托马斯进动使自旋轨道耦合修正出现半因子。

  - internal_id: hyperfine_structure
    display_zh: 超精细结构
    category: physics_model
    aliases: ["氢21厘米线", "hyperfine structure"]
    description: 核磁矩与电子磁矩相互作用造成更小能级劈裂。

  - internal_id: fermi_contact_interaction
    display_zh: 费米接触项
    category: physics_law
    aliases: ["接触相互作用", "Fermi contact"]
    description: s态电子在原点概率密度导致磁偶极接触能。

  - internal_id: magnetic_dipole_hamiltonian
    display_zh: 磁偶极哈密顿量
    category: physics_law
    aliases: ["偶极相互作用", "dipole Hamiltonian"]
    description: 用磁偶极子在磁场中的能量计算能级修正。

  - internal_id: perturbation_energy_shift
    display_zh: 微扰能级修正
    category: math_technique
    aliases: ["一级微扰", "perturbation shift"]
    description: 用未扰动波函数期望值求小相互作用能级位移。

  - internal_id: fermi_gas_nucleus
    display_zh: 核费米气体
    category: physics_model
    aliases: ["费米气体模型", "nuclear Fermi gas"]
    description: 将核子视作势阱中简并费米气体估算核性质。

  - internal_id: semi_empirical_mass_formula
    display_zh: 半经验质量公式
    category: physics_model
    aliases: ["液滴模型公式", "Bethe-Weizsäcker"]
    description: 用体积、表面、库仑等项估算原子核结合能。

  - internal_id: beta_decay_spectrum
    display_zh: β衰变谱
    category: physics_model
    aliases: ["连续β谱", "beta spectrum"]
    description: 用三体末态相空间解释β衰变电子连续能谱。

  - internal_id: decay_branching_ratio
    display_zh: 衰变分支比
    category: physics_law
    aliases: ["branching ratio", "分支衰变"]
    description: 比较不同末态衰变常数确定各通道概率。

  - internal_id: crystal_photoelectric_effect
    display_zh: 晶体光电效应
    category: physics_model
    aliases: ["晶体中光电发射", "crystal photoeffect"]
    description: 考虑晶格周期性对光电子动量与能量的影响。

  - internal_id: reciprocal_lattice_momentum
    display_zh: 倒格矢动量
    category: physics_law
    aliases: ["晶格动量", "reciprocal vector"]
    description: 晶体中动量守恒可相差一个倒格矢。
