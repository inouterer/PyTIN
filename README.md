# PyTIN
Маленькая библиотека для работы с нерегулярной поверхностью. Позволяет:
- по набору точек создать триангуляцию Делоне слегка опримизированным алгоритмом Боуэра — Ватсона;
- определить уровни и построить изолинии с помощью линейной интерполяции;
- сгладить изолинии кубическим сплайном Хермита;
- построить по сглаженным и несглаженным изолиниям замкнутые изоконтуры.
- визуализировать результат.


![Триангуляция, изолинии и сглаженные изолинии](images/trn.jpg)

![Изоконтуры](images/iso.jpg)

Зависимости: matplotlib для визуализации