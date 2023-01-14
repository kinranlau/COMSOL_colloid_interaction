from os.path import join, dirname
import pandas as pd
# ignore pandas chained assignment warning
pd.options.mode.chained_assignment = None  # default='warn'

# import all header names
from headers import *

#%%
# import results.csv
my_csv = 'results.csv'
results = pd.read_csv(join(dirname(__file__), my_csv))
#%%
# Parameters which are varied
# 1. colloid height
# 2. colloid radius
# 3. conc.
# 4. V_particle
# 5. V_defect
# 6. V_surface
# 7. defect density

colloid_height_unique = sorted(results[label_with_unit['colloid_height_debye']].unique())
colloid_radius_unique = sorted(results[label_with_unit['rel_radius']].unique())

conc_unique = sorted(results[label_with_unit['conc']].unique())

V_particle_unique =  sorted(results[label_with_unit['particle_potential_dless']].unique())
V_defect_unique =  sorted(results[label_with_unit['defect_potential_dless']].unique())
V_surface_unique =  sorted(results[label_with_unit['surface_potential_dless']].unique())

DD_unique = sorted(results[label_with_unit['def_density']].unique())


# import bokeh packages
from bokeh.layouts import column, row, grid
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, Div, Select, Slider, HoverTool
from bokeh.palettes import Dark2
from bokeh.io import curdoc

# define the colour palatte for the graphs
# use Dark2 as the basic palette
dark2 = list(Dark2[8])
color_p = dark2[:2]
# navy for normal surface
color_p.append('#00007f')
# grey for bulk electrolyte
color_p.append(dark2[-1])
# but we want to use Fel (blue) + vdw (yellow) = TotalE (green)
# blue
color_p.append('#0066cc')
# yellow
color_p.append(dark2[5])
# green
color_p.append(dark2[4])

# Description/Title of the plot
defect_radius = 0.5
avg_pot = 0     # will get updated with selected parameters

para_desc = Div(text = '''
                <h2> Parameters: </h2>
                ''')

defect_desc = Div(text = f'''
                    Defect radius (L<sub>D</sub>) = {defect_radius:.1f} nm 
                    <br> <br>
                ''')

avg_pot_desc = Div(text = f'''
                   (Surface + Defect) potential = {avg_pot:.3f} <br> <br>
                   ''')
                   
hamaker_desc = Div(text = f'''
                   Hamaker constant (zJ) in water: <br>
                   TiO<sub>2</sub> - TiO<sub>2</sub>: ~ 50-60 <br>
                   Au - Au: ~ 90-300
                   ''')

# Create Input controls (selectors)
# sliders might need to rounding off problems...
# that's why decided to use selector instead, but have to convert between string and float!
# 1. colloid height
# 2. colloid radius
# 3. conc.
# 4. V_particle
# 5. V_defect
# 6. V_surface
# 7. defect density

# 8. vdw Hamaker constant
title_radius = Div(text="$$R$$: Particle radius (L<sub>D</sub>)")
slider_radius = Select(title= "", options= [str(num) for num in colloid_radius_unique], value=str(colloid_radius_unique[2]))

title_conc = Div(text="$$Conc$$: Concentration (mM)")
slider_conc = Select(title="", options= [str(num) for num in conc_unique], value=str(conc_unique[-1]))

title_particleV = Div(text="$$V_{Part}$$: Particle potential (dimensionless)")
slider_particleV = Select(title="", options= [str(num) for num in V_particle_unique], value=str(V_particle_unique[0]))

title_defectV = Div(text="$$V_{Def}$$: Defect potential (dimensionless)")
slider_defectV = Select(title="", options= [str(num) for num in V_defect_unique], value=str(V_defect_unique[1]))

title_surfaceV = Div(text="$$V_{Surf}$$: Surface potential (dimensionless)")
slider_surfaceV = Select(title="", options= [str(num) for num in V_surface_unique], value=str(V_surface_unique[0]))

title_defect_density = Div(text="$$DD$$: Defect density (/)")
slider_defect_density = Select(title="", options= [str(num) for num in DD_unique], value=str(DD_unique[2]))

title_vdw = Div(text="$$A_H$$: Hamaker constant (zJ)")
slider_vdw = Slider(title="", start=0, end=200, value=100, step=1)

# Create a "dummy"/"framework" of the Column Data Source to be plotted later with the selected DataFrame
config = ColumnDataSource(data=dict(height_map=[], 
                                    particle_map=[],
                                    defect_map=[],
                                    norm_surf_map =[],
                                    vol_sum_map=[],
                                    Fel_map = [],
                                    vdw_map = [],
                                    tot_energy_map = []))

# define x and y axis labels
x_axis = 'Particle-Surface separation (Debye length)'
y_axis = 'Energy (kT)'

# Set the 'dummy structure' for the plots
# 1st row : surface and volume  contribution
# Particle surf
def particle_p():
    particle_p = figure(height=300)
    particle_p.title.text = "Particle"
    particle_p.title.text_color = color_p[0]
    particle_p.title.align = "center"
    particle_p.xaxis.axis_label = x_axis
    particle_p.yaxis.axis_label = y_axis
    
    circles = particle_p.circle(x = 'height_map', y = 'particle_map', source = config, size = 4, color=color_p[0])
    line = particle_p.line(x = 'height_map', y = 'particle_map', source = config, color=color_p[0])
    
    hover_tool = HoverTool(tooltips=[
            (y_axis, '$y'),
        ], renderers=[line])
    particle_p.tools.append(hover_tool)

    return particle_p

# Defect surf
def defect_p():
    defect_p = figure(height=300)
    defect_p.title.text = "Defects"
    defect_p.title.text_color = color_p[1]
    defect_p.title.align = "center"
    defect_p.xaxis.axis_label = x_axis
    defect_p.yaxis.axis_label = y_axis
    
    circles = defect_p.circle(x = 'height_map', y = 'defect_map', source = config, size = 4, color=color_p[1])
    line = defect_p.line(x = 'height_map', y = 'defect_fit_map', source = config, color=color_p[1])
    
    hover_tool = HoverTool(tooltips=[
            (y_axis, '$y'),
        ], renderers=[line])
    defect_p.tools.append(hover_tool)
    
    return defect_p

# Normal surf
def norm_surf_p():
    norm_surf_p = figure(height=300)
    norm_surf_p.title.text = "Normal surface"
    norm_surf_p.title.text_color = color_p[2]
    norm_surf_p.title.align = "center"
    norm_surf_p.xaxis.axis_label = x_axis
    norm_surf_p.yaxis.axis_label = y_axis
    
    circles = norm_surf_p.circle(x = 'height_map', y = 'norm_surf_map', source = config, size = 4, color=color_p[2])
    line = norm_surf_p.line(x = 'height_map', y = 'norm_surf_fit_map', source = config, color=color_p[2])
    
    hover_tool = HoverTool(tooltips=[
            (y_axis, '$y'),
        ], renderers=[line])
    norm_surf_p.tools.append(hover_tool)
    
    return norm_surf_p

# Krishnan vol
def Vol_p():
    Vol_p = figure(height=300)
    Vol_p.title.text = "Electrolyte volume"
    Vol_p.title.text_color = color_p[3]
    Vol_p.title.align = "center"
    Vol_p.xaxis.axis_label = x_axis
    Vol_p.yaxis.axis_label = y_axis
    
    circles = Vol_p.circle(x = 'height_map', y = 'vol_sum_map', source = config, size = 4, color=color_p[3])
    line = Vol_p.line(x = 'height_map', y = 'vol_sum_map', source = config, color=color_p[3])
    
    hover_tool = HoverTool(tooltips=[
            (y_axis, '$y'),
        ], renderers=[line])
    Vol_p.tools.append(hover_tool)    
    
    return Vol_p


# 2nd row: Fel and vdw and total free energy
# Fel electrostatic free energy
def Fel_p():
    Fel_p = figure(height=300)
    Fel_p.title.text = "Electrostatic free energy (Fel)"
    Fel_p.title.text_color = color_p[4]
    Fel_p.title.align = "center"
    Fel_p.xaxis.axis_label = x_axis
    Fel_p.yaxis.axis_label = y_axis
    
    circles = Fel_p.circle(x = 'height_map', y = 'Fel_map', source = config, size = 4, color=color_p[4])
    line = Fel_p.line(x = 'height_map', y = 'Fel_map', source = config, color=color_p[4])

    hover_tool = HoverTool(tooltips=[
            (y_axis, '$y'),
        ], renderers=[line])
    Fel_p.tools.append(hover_tool)    
    
    return Fel_p

# vdw
def vdw():
    vdw = figure(height=300)
    vdw.title.text = "Van der Waals energy"
    vdw.title.text_color = color_p[5]
    vdw.title.align = "center"
    vdw.xaxis.axis_label = x_axis
    vdw.yaxis.axis_label = y_axis
    
    circles = vdw.circle(x = 'height_map', y = 'vdw_map', source = config, size = 4, color=color_p[5])
    line = vdw.line(x = 'height_map', y = 'vdw_map', source = config, color=color_p[5])
    
    hover_tool = HoverTool(tooltips=[
            (y_axis, '$y'),
        ], renderers=[line])
    vdw.tools.append(hover_tool)    
    
    return vdw


# total free energy
def tot_energy_p():
    tot_energy_p = figure(height=300)
    tot_energy_p.title.text = "Total energy =  Fel + vdw"
    tot_energy_p.title.text_color = color_p[6]
    tot_energy_p.title.align = "center"
    tot_energy_p.xaxis.axis_label = x_axis
    tot_energy_p.yaxis.axis_label = y_axis
    
    circles = tot_energy_p.circle(x = 'height_map', y = 'tot_energy_map', source = config, size = 4, color=color_p[6])
    line = tot_energy_p.line(x = 'height_map', y = 'tot_energy_map', source = config, color=color_p[6])

    hover_tool = HoverTool(tooltips=[
            (y_axis, '$y'),
        ], renderers=[line])
    tot_energy_p.tools.append(hover_tool)    
    
    return tot_energy_p

l = grid([
    [particle_p(), defect_p(), norm_surf_p(), Vol_p()],
    [Fel_p(), vdw(), tot_energy_p()],
], sizing_mode='stretch_width')

#show(l)


# A function to filter the DataFrame with the specific configurations in question (e.g. particle radius, defect potential)
# Then use this selected DataFrame to plot and update the graphs
def select_parameters():
    
    radius_val = float(slider_radius.value)
    conc_val = float(slider_conc.value)
    particleV_val = float(slider_particleV.value)
    defectV_val = float(slider_defectV.value)
    surfaceV_val = float(slider_surfaceV.value)
    defect_den_val = float(slider_defect_density.value)
    
    hamaker_val = slider_vdw.value
    # for the case without defects, Vdefect = 0 and defect density = 0
    # we want to bundle them together so changing one will update another immediately
    if defectV_val == V_defect_unique[0]:
        defect_den_val = DD_unique[0]
        
    if defect_den_val == DD_unique[0]:
        defectV_val = V_defect_unique[0]  
    
    selected_df = results[\
    (results[label_with_unit['rel_radius']] == radius_val) & \
    (results[label_with_unit['conc']] == conc_val) & \
    (results[label_with_unit['particle_potential_dless']] == particleV_val) & \
    (results[label_with_unit['defect_potential_dless']] == defectV_val) & \
    (results[label_with_unit['surface_potential_dless']] == surfaceV_val) & \
    (results[label_with_unit['def_density']] == defect_den_val)]

    selected_df = selected_df.sort_values(label_with_unit['colloid_height_debye'])
    
    # average surface potential
    avg_pot = selected_df[label_with_unit['average_surface_potential']].iloc[-1]
    
    # vdw = - (hamaker * r) / (6d)
    vdw = - (hamaker_val * 1e-21 * selected_df[label_with_unit['colloid_radius']]) / (6.0 * selected_df[label_with_unit['colloid_height_debye']] * selected_df[label_with_unit['debye']])
    vdw_kT = vdw / (kb*298)
    selected_df['van der Waals energy / kT'] = vdw_kT
    
    # Interaction energy = Fel + vdw
    selected_df['Total intereaction energy / kT']= selected_df[label_with_unit['Fel']] + selected_df['van der Waals energy / kT']
    
    # let's also drop all other irrelevant columns
    # and also rename them to shorter names
    selected_df_drop = selected_df[[label_with_unit['colloid_height_debye'],
                                    label_with_unit['particle_kT'],
                                    label_with_unit['defect_kT'],
                                    label_with_unit['defect_kT_fit'],
                                    label_with_unit['suf_kT'],
                                    label_with_unit['suf_kT_fit'],
                                    label_with_unit['tot_surf_energy'],
                                    label_with_unit['tot_vol_energy'],
                                    label_with_unit['Fel'],
                                    'van der Waals energy / kT',
                                    'Total intereaction energy / kT'
                                    ]]
    
    selected_df_drop.rename(columns={label_with_unit['colloid_height_debye']: 'height_map',
                   label_with_unit['particle_kT']: 'particle_map',
                   label_with_unit['defect_kT']: 'defect_map',
                   label_with_unit['defect_kT_fit']: 'defect_fit_map',
                   label_with_unit['suf_kT']: 'norm_surf_map',
                   label_with_unit['suf_kT_fit']: 'norm_surf_fit_map',
                   label_with_unit['tot_surf_energy']: 'surf_sum_map',
                   label_with_unit['tot_vol_energy']: 'vol_sum_map',
                   label_with_unit['Fel']: 'Fel_map',
                   'van der Waals energy / kT': 'vdw_map',
                   'Total intereaction energy / kT': 'tot_energy_map'},
          inplace=True)
    
    return selected_df_drop, avg_pot


# An update function to i) filter the DataFrame ii) update the data source to be plotted
def update():
    df, avg_pot = select_parameters()
    
    # update graphs
    config.data = dict(
        height_map = df['height_map'], 
        particle_map = df['particle_map'],
        defect_map = df['defect_map'],
        defect_fit_map = df['defect_fit_map'],
        norm_surf_map = df['norm_surf_map'],
        norm_surf_fit_map = df['norm_surf_fit_map'],
        surf_sum_map = df['surf_sum_map'],
        vol_sum_map = df['vol_sum_map'],
        Fel_map = df['Fel_map'],
        vdw_map = df['vdw_map'],
        tot_energy_map = df['tot_energy_map'])
    
    # update average potential
    avg_pot_desc.text = f'''
                   (Surface + Defect) potential = {avg_pot:.3f} <br> <br>
                   '''
    
    
    
# Comply all the sliders and plots together    
controls = [slider_particleV, slider_surfaceV, slider_defectV, slider_defect_density, slider_conc, slider_radius, slider_vdw]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())
 
    
inputs = column(
    # Parameter
    para_desc, 
    # Particle, Surface, Defect potential
    title_particleV, controls[0], title_surfaceV, controls[1], title_defectV, controls[2], avg_pot_desc, 
    # DD, Conc, R
    title_defect_density, controls[3], title_conc, controls[4], title_radius, controls[5], defect_desc,
    # Hamaker
    title_vdw, controls[6], hamaker_desc,
    # width
    width=320)

#show(inputs)

plot = row(inputs, l, sizing_mode="scale_height")

update()  # initial load of the data

curdoc().add_root(plot)
curdoc().title = "Energy plots"