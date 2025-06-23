import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("Beam and Half-Cylinder Concrete Visualizer")

st.sidebar.header("Beam and Concrete Parameters")
unit_system = st.sidebar.selectbox("Select unit system:", ["SI (m)", "Imperial (in)"])

INCH_TO_M = 0.0254

def to_si(val, from_unit):
    if from_unit == 'in':
        return val * INCH_TO_M
    else:
        return val

def from_si(val, to_unit):
    if to_unit == 'in':
        return val / INCH_TO_M
    else:
        return val

if unit_system == "SI (m)":
    x = st.sidebar.number_input("Beam Width x (m)", min_value=0.01, value=0.15, step=0.01, format="%.3f")
    y = st.sidebar.number_input("Beam Length y (m)", min_value=0.01, value=0.30, step=0.01, format="%.3f")
    z = st.sidebar.number_input("Beam Height z (m)", min_value=0.01, value=0.30, step=0.01, format="%.3f")
    clearance = st.sidebar.number_input("Clearance (m)", min_value=0.0, value=0.05, step=0.01, format="%.3f")
    shell_height = st.sidebar.number_input("Shell Height (m)", min_value=0.01, value=0.60, step=0.01, format="%.3f")
    shell_thickness = st.sidebar.number_input("Shell Thickness (m)", min_value=0.005, value=0.05, step=0.005, format="%.3f")
else:
    x = to_si(st.sidebar.number_input("Beam Width x (in)", min_value=0.1, value=6.0, step=0.1, format="%.2f"), 'in')
    y = to_si(st.sidebar.number_input("Beam Length y (in)", min_value=0.1, value=12.0, step=0.1, format="%.2f"), 'in')
    z = to_si(st.sidebar.number_input("Beam Height z (in)", min_value=0.1, value=12.0, step=0.1, format="%.2f"), 'in')
    clearance = to_si(st.sidebar.number_input("Clearance (in)", min_value=0.0, value=2.0, step=0.1, format="%.2f"), 'in')
    shell_height = to_si(st.sidebar.number_input("Shell Height (in)", min_value=0.1, value=24.0, step=0.1, format="%.2f"), 'in')
    shell_thickness = to_si(st.sidebar.number_input("Shell Thickness (in)", min_value=0.2, value=2.0, step=0.1, format="%.2f"), 'in')

# Calculate required half-cylinder radius
diag = np.sqrt(x**2 + (z/2)**2)
a = diag + clearance  # Inner radius from wall to farthest beam corner plus clearance

st.info(f"""
### Current Design Parameters
- **Beam width (x):** {from_si(x, 'in'):.2f} in
- **Beam length (y):** {from_si(y, 'in'):.2f} in
- **Beam height (z):** {from_si(z, 'in'):.2f} in
- **Clearance:** {from_si(clearance, 'in'):.2f} in
- **Shell height:** {from_si(shell_height, 'in'):.2f} in
- **Shell thickness:** {from_si(shell_thickness, 'in'):.2f} in
- **Required inner radius (a):** {from_si(a, 'in'):.2f} in

_The half-cylinder should have at least this inner radius to fit the beam with the specified clearance._
""")

# 3D Visualization
st.subheader("3D Visualization")
theta = np.linspace(-np.pi/2, np.pi/2, 100)
Z_shell = np.linspace(0, shell_height, 30)
Theta, Zgrid_shell = np.meshgrid(theta, Z_shell)
X_inner = a * np.cos(Theta)
Y_inner = a * np.sin(Theta)
Z_inner = Zgrid_shell

fig = go.Figure()
fig.add_trace(go.Surface(
    x=X_inner, y=Y_inner, z=Z_inner,
    surfacecolor=np.full_like(X_inner, 0.5),
    cmin=0, cmax=1,
    colorscale=[[0, 'lightgray'], [1, 'lightgray']],
    showscale=False,
    opacity=0.85,
    name='Inner Surface (Beam Clearance)'
))

# Outer wall (user-selected thickness)
X_outer = (a + shell_thickness) * np.cos(Theta)
Y_outer = (a + shell_thickness) * np.sin(Theta)
Z_outer = Zgrid_shell
fig.add_trace(go.Surface(
    x=X_outer, y=Y_outer, z=Z_outer,
    surfacecolor=np.full_like(X_outer, 0.2),
    cmin=0, cmax=1,
    colorscale=[[0, 'gainsboro'], [1, 'gainsboro']],
    showscale=False,
    opacity=0.25,
    name='Outer Surface (Shell Face)'
))

# Flat back (vertical plane at x=0 from y=-(a+shell_thickness) to y=+(a+shell_thickness))
b = a + shell_thickness
Y_flat = np.linspace(-b, b, 30)
Z_flat = np.linspace(0, shell_height, 30)
Y_flat_grid, Z_flat_grid = np.meshgrid(Y_flat, Z_flat)
X_flat = np.zeros_like(Y_flat_grid)
fig.add_trace(go.Surface(
    x=X_flat, y=Y_flat_grid, z=Z_flat_grid,
    surfacecolor=np.full_like(X_flat, 0.1),
    cmin=0, cmax=1,
    colorscale=[[0, 'gainsboro'], [1, 'gainsboro']],
    showscale=False,
    opacity=0.25,
    name='Flat Back'
))

# Beam (as a box, back at x=0, width x, length y, height z)
beam_vertices = np.array([
    [0, -y/2, 0], [x, -y/2, 0], [x, y/2, 0], [0, y/2, 0],
    [0, -y/2, z], [x, -y/2, z], [x, y/2, z], [0, y/2, z]
])
# Define triangles for all 6 faces (2 triangles per face)
beam_i = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
beam_j = [1, 3, 2, 0, 3, 1, 0, 2, 5, 7, 6, 4]
beam_k = [3, 2, 3, 1, 1, 0, 2, 0, 7, 6, 7, 5]
fig.add_trace(go.Mesh3d(
    x=beam_vertices[:,0],
    y=beam_vertices[:,1],
    z=beam_vertices[:,2],
    i=beam_i,
    j=beam_j,
    k=beam_k,
    color='saddlebrown',
    opacity=0.7,
    name='Beam',
    showscale=False
))

fig.update_layout(
    scene=dict(
        xaxis_title=f'X ({"in" if unit_system != "SI (m)" else "m"})',
        yaxis_title=f'Y ({"in" if unit_system != "SI (m)" else "m"})',
        zaxis_title=f'Z ({"in" if unit_system != "SI (m)" else "m"})',
        aspectmode='data',
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    showlegend=True
)
st.plotly_chart(fig, use_container_width=True)

# Graph: Required radius vs. beam width for fixed height and clearance
st.subheader("Required Radius vs. Beam Width")
beam_widths = np.linspace(to_si(2.0, 'in'), to_si(12.0, 'in'), 50)
radii = np.sqrt(beam_widths**2 + (z/2)**2) + clearance
radii_out = from_si(radii, 'in') if unit_system != 'SI (m)' else radii
beam_widths_out = from_si(beam_widths, 'in') if unit_system != 'SI (m)' else beam_widths

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=beam_widths_out,
    y=radii_out,
    mode='lines+markers',
    name='Required Inner Radius',
    hovertemplate='Beam Width: %{x:.2f}<br>Inner Radius: %{y:.2f}'
))
fig2.update_layout(
    xaxis_title=f'Beam Width ({"in" if unit_system != "SI (m)" else "m"})',
    yaxis_title=f'Required Inner Radius ({"in" if unit_system != "SI (m)" else "m"})',
    title='Required Half-Cylinder Radius vs. Beam Width',
    hovermode='x unified'
)
st.plotly_chart(fig2, use_container_width=True) 