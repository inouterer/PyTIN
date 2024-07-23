import ezdxf
import plotly.graph_objects as go

# Чтение файла DXF
doc = ezdxf.readfile("input_data\\kgs2.dxf")
msp = doc.modelspace()

# Извлечение координат начальной и конечной точек для каждой линии из файла DXF
lines = [(line.dxf.start, line.dxf.end) for line in msp.query('LINE')]

# Создание списка для хранения данных о линиях для Plotly
line_data = []
for start, end in lines:
    x = [start[0], end[0]]
    y = [start[1], end[1]]
    line_data.append(go.Scatter(x=x, y=y, mode='lines', line=dict(color='gray')))

# Создание графика Plotly
fig = go.Figure(data=line_data)

# Настройка макета графика
fig.update_layout(title='Изоконтуры и точки с подписями',
    xaxis_title='X',
    yaxis_title='Y',
    xaxis_scaleanchor='y',
    yaxis_scaleanchor='x',
    showlegend=False)

# Отображение графика

fig.show()