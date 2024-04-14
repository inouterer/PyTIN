point_in = [14551170,7664797,121,
14551343,7664809,126,
14551590,7664839,133,
14551745,7664863,135,
14551969,7664885,139,
14552109,7664893,139,
14552144,7664730,137,
14551916,7664696,145,
14551656,7664670,144,
14551440,7664652,139,
14551207,7664625,129,
14551396,7664576,144,
14551226,7664457,127,
14551400,7664331,129,
14551732,7664363,147,
14551827,7664499,148,
14551935,7664599,145,
14551643,7664552,139,
14551519,7664484,132,
14551393,7664417,130,
14551239,7664343,123,
14551241,7664194,130,
14551386,7664208,133,
14551518,7664217,138,
14551644,7664206,142,
14551561,7664381,137,
14551606,7664310,142,
14551792,7664258,141,
14551970,7664256,139,
14552153,7664267,132,
14552144,7664525,137,
14552006,7664425,141,
14551870,7664387,144,
14551663,7664459,142,
14551802,7664664,145,
14551862,7664857,136,
14551486,7664769,133,
14551312,7664705,130,
14551309,7664581,140,
14551773,7664585,146,
14551535,7664609,141,
14552055,7664781,140]

trn_in = [22,24,21,
    22,23,24,
    27,28,24,
    29,24,28,
    23,26,24,
    13,23,22,
    24,14,27,
    20,22,21,
    26,14,24,
    20,13,22,
    32,28,27,
    23,25,26,
    13,25,23,
    14,32,27,
    31,29,28,
    32,31,28,
    20,19,13,
    26,33,14,
    25,33,26,
    19,25,13,
    19,18,25,
    12,19,20,
    14,15,32,
    31,30,29,
    18,33,25,
    33,15,14,
    15,31,32,
    18,17,33,
    38,19,12,
    11,18,19,
    38,11,19,
    33,39,15,
    15,16,31,
    17,39,33,
    40,17,18,
    10,38,12,
    11,40,18,
    16,30,31,
    9,40,11,
    39,16,15,
    34,16,39,
    8,39,17,
    40,8,17,
    34,7,16,
    10,37,38,
    37,11,38,
    8,34,39,
    37,9,11,
    16,6,30,
    36,40,9,
    16,41,6,
    7,41,16,
    36,8,40,
    0,37,10,
    1,9,37,
    1,36,9,
    36,2,8,
    34,35,7,
    8,3,34,
    0,1,37,
    3,35,34,
    2,3,8,
    7,4,41,
    35,4,7,
    5,6,41,
    4,5,41,
    1,2,36,
    3,4,35,
    21,12,20,
    12,0,10,
    21,0,12,
    6,29,30,
    0,2,1,
    0,3,2]

real_levels = [-20,-15,-10,-7,-5,-3,-1.5,-0.5,0,0.5,1.5,3,5,7,10]

real = [8648.34	,	16452.61	,	20.8	,
8655.17	,	16493.29	,	11.4	,
8597.97	,	16495.91	,	-12	,
8591.83	,	16460.64	,	-95.5	,
8647.73	,	16451.44	,	4.3	,
8627.78	,	16466.78	,	-60	,
8654.96	,	16492.71	,	2.1	,
8637.69	,	16495.88	,	-32.6	,
8610.09	,	16469.86	,	-79.6	,
8608.38	,	16458.15	,	-88.7	,
8593.68	,	16479.42	,	-56.8	,
8596.7	,	16495.76	,	-45.3	,
8649.66	,	16462.35	,	6.9	,
8636.34	,	16453.28	,	-6.7	,
8591.87	,	16467.41	,	-40.4	,
8595.97	,	16491.72	,	-16.3	,
8605.53	,	16494.22	,	-27.5	,
8619.95	,	16493.23	,	-30	,
8648.92	,	16493.94	,	-0.9	,
8652.84	,	16481.22	,	3.4	,
8577.33	,	16463.75	,	-29	,
8580.45	,	16481.73	,	-29.3	,
8582.92	,	16495.85	,	-33.3	,
8584.53	,	16505.06	,	-41.7	,
8567.46	,	16498.54	,	-27.9	,
8558.72	,	16485.67	,	-23	,
8536.8	,	16496.61	,	-28.4	,
8524.76	,	16498.71	,	-18.7	,
8494.79	,	16504.52	,	-32.2	,
8497.28	,	16518.67	,	-21.6	,
8500.61	,	16538.03	,	-7	,
8479.48	,	16542	,	-2.5	,
8474.68	,	16515.33	,	-26.5	,
8468.96	,	16482.65	,	-33.6	,
8490.11	,	16478.78	,	-58.9	,
8491.24	,	16478.58	,	-57.9	,
8502.07	,	16470.61	,	-62	,
8548.6	,	16462.48	,	-25	,
8560.82	,	16466.42	,	-20.5	,
8562.02	,	16466.22	,	-24.1	,
8547.53	,	16487.65	,	-12.2	,
8536.81	,	16464.55	,	-13.4	,
8525.04	,	16466.73	,	-16.8	,
8510.3	,	16469.18	,	-24.4	,
8512.07	,	16494.23	,	-18.8	,
8500.4	,	16495.86	,	-22.4	,
8499.08	,	16529.09	,	-7.4	,
8489.31	,	16540.29	,	-3	,
8477.15	,	16529.5	,	-5.7	,
8473.31	,	16508.26	,	-8.7	,
8470.99	,	16494.12	,	-11.9	,
8478.31	,	16480.82	,	-25.8	,
8572.32	,	16464.05	,	-4.2	,
8562.98	,	16465.67	,	-2.9	,
8558.53	,	16466.45	,	-3.5	,
8492.31	,	16478.02	,	-23.7	,
8489.56	,	16478.5	,	-25.6	,
8474.63	,	16481.1	,	-22.9	,
8480.99	,	16542.1	,	7.6	,
8500.33	,	16538.73	,	12.6	,
8565.66	,	16490.47	,	2.1	,
8571.73	,	16512.17	,	-13.1	,
8584.08	,	16506.7	,	-13.9]