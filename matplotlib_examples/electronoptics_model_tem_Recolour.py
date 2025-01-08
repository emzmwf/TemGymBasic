from temgymbasic import components as comp
from temgymbasic.model import Model
#from temgymbasic.run import show_matplotlib
import temgymbasic.shapes

#NOTE - this requires a change of source from supplied, 
# components.py change at line 463
#        if sample is not None:
#            self.sample_pixels = sample.shape[0]

# NOTE2 - colours are currently hardcoded for the package in run.py
# lines 524-526, to overcome this need to run in the script:

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

def show_matplotlib(model, name = 'model.svg', component_lw = 4, edge_lw = 1, label_fontsize = 20):
    '''Code to show a matplotlib model

    Parameters
    ----------
    model : class
        Microscope Model
    name : str, optional
        Name of file, by default 'model.svg'
    component_lw : int, optional
        Linewidth of component outline, by default 4
    edge_lw : int, optional
        Linewidth of highlight to edges, by default 1
    label_fontsize : int, optional
        Fontsize of labels, by default 20

    Returns
    -------
    fig : class
        Matplotlib figure object
    ax : class
        Matplotlib axis object of the figure
    '''    
    #Step the rays through the model to get the ray positions throughout the column
    rays = model.step()

    #Collect their x, y & z coordinates
    x, y, z = rays[:, 0, :], rays[:, 2, :], model.z_positions

    #Create a figure
    fig, ax = plt.subplots(figsize=(12, 20))

    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.grid(color='lightgrey', linestyle='--', linewidth=0.5)
    ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
    ax.set_yticks([])
    ax.set_yticklabels([])
    
    ax.get_xaxis().set_ticks(
        [-model.detector_size/2, 0, model.detector_size/2])
    ax.set_xlim([-0.5, 0.5])
    ax.set_ylim([0, model.beam_z])
    ax.set_aspect('equal', adjustable='box')
    ax.text(0, model.beam_z, 'Electron Gun', fontsize=label_fontsize, zorder = 1000)
    
    #Set starting index of component so that we can plot rays from one component to the next
    idx = 1

    #Generate a list of the allowed rays, so we can block them when they hit an aperture
    allowed_rays = range(model.num_rays)
    
    #Set colors of rays
    ray_color = 'dimgray'
    fill_color = 'palegreen'
    fill_color_pair = ['khaki', 'chartreuse']

    fill_alpha = 1
    ray_alpha = 1

    ray_lw = 0.25

    plot_rays = True
    highlight_edges = True
    fill_between = True

    edge_rays = [0, model.num_rays-1]
    label_x = 0.30
    
    #Loop through components, and for each type of component plot rays in the correct ray,
    #and increment the index correctly
    for component in model.components:
        if allowed_rays != []:
            if highlight_edges == True:
                ax.plot(x[idx-1:idx+1, edge_rays], z[idx-1:idx+1],
                        color='k', linewidth=edge_lw, alpha=1, zorder=2)
            if fill_between == True:
                pair_idx = 0
                for first, second in zip(edge_rays[::2], edge_rays[1::2]):
                    if len(edge_rays) == 4:
                        ax.fill_betweenx(z[idx-1:idx+1], x[idx-1:idx+1, first], x[idx-1:idx+1, second],
                                         color=fill_color_pair[pair_idx], edgecolor=fill_color_pair[pair_idx], alpha=fill_alpha, zorder=0, lw=None)
                        pair_idx += 1
                    else:
                        ax.fill_betweenx(z[idx-1:idx+1], x[idx-1:idx+1, first], x[idx-1:idx+1, second],
                                         color=fill_color, edgecolor=fill_color, alpha=fill_alpha, zorder=0, lw=None)
            if plot_rays == True:
                ax.plot(x[idx-1:idx+1, allowed_rays], z[idx-1:idx+1],
                        color=ray_color, linewidth=ray_lw, alpha=ray_alpha, zorder=1)

        if component.type == 'Biprism':
            ax.text(label_x, component.z-0.01,
                    component.name, fontsize=label_fontsize, zorder = 1000)

            if model.beam_type == 'x_axial' and component.theta == 0:
                ax.plot(component.points[0, :], component.points[2,
                        :], color='dimgrey', alpha=0.8, linewidth=component_lw)
            elif model.beam_type == 'x_axial' and component.theta == np.pi/2:
                ax.add_patch(plt.Circle((0, component.z), component.width,
                             edgecolor='k', facecolor='w', zorder=1000))

            idx += 1
        elif component.type == 'Quadrupole':
            r = component.radius
            ax.text(label_x, component.z-0.01, 'Upper ' +
                    component.name, fontsize=label_fontsize, zorder = 1000)
            ax.plot([-r, -r/2], [z[idx], z[idx]],
                    color='lightcoral', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([-r/2, 0], [z[idx], z[idx]],
                    color='lightblue', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([0, r/2], [z[idx], z[idx]],
                    color='lightcoral', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([r/2, r], [z[idx], z[idx]],
                    color='lightblue', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([-r, r], [z[idx], z[idx]],
                    color='k', alpha=0.8, linewidth=component_lw+2, zorder=998)
            idx += 1

        elif component.type == 'Aperture':
            ax.text(label_x, component.z-0.01,
                    component.name, fontsize=label_fontsize, zorder = 1000)
            ri = component.aperture_radius_inner
            ro = component.aperture_radius_outer

            ax.plot([-ri, -ro], [z[idx], z[idx]],
                    color='dimgrey', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([ri, ro], [z[idx], z[idx]],
                    color='dimgrey', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([-ri, -ro], [z[idx], z[idx]],
                    color='k', alpha=1, linewidth=component_lw+2, zorder=998)
            ax.plot([ri, ro], [z[idx], z[idx]],
                    color='k', alpha=1, linewidth=component_lw+2, zorder=998)

            idx += 1
        elif component.type == 'Double Deflector':
            r = component.radius
            ax.text(label_x, component.z_up-0.01, 'Upper ' +
                    component.name, fontsize=label_fontsize, zorder = 1000)
            ax.plot([-r, 0], [z[idx], z[idx]],
                    color='lightcoral', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([0, r], [z[idx], z[idx]],
                    color='lightblue', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([-r, r], [z[idx], z[idx]],
                    color='k', alpha=0.8, linewidth=component_lw+2, zorder=998)
            idx += 1

            if allowed_rays != []:
                if highlight_edges == True:
                    ax.plot(x[idx-1:idx+1, edge_rays], z[idx-1:idx+1],
                            color='k', linewidth=edge_lw, alpha=1, zorder=2)
                if fill_between == True:
                    pair_idx = 0
                    for first, second in zip(edge_rays[::2], edge_rays[1::2]):
                        if len(edge_rays) == 4:
                            ax.fill_betweenx(z[idx-1:idx+1], x[idx-1:idx+1, first], x[idx-1:idx+1,
                                             second], color=fill_color_pair[pair_idx], alpha=fill_alpha, zorder=1)
                            pair_idx += 1
                        else:
                            ax.fill_betweenx(z[idx-1:idx+1], x[idx-1:idx+1, first], x[idx -
                                             1:idx+1, second], color=fill_color, alpha=fill_alpha, zorder=0)
                if plot_rays == True:
                    ax.plot(x[idx-1:idx+1, allowed_rays], z[idx-1:idx+1],
                            color=ray_color, linewidth=ray_lw, alpha=ray_alpha, zorder=1)

            ax.text(label_x, component.z_low-0.01,
                    'Lower ' + component.name, fontsize=label_fontsize, zorder = 1000)
            ax.plot([-r, 0], [z[idx], z[idx]],
                    color='lightcoral', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([0, r], [z[idx], z[idx]],
                    color='lightblue', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([-r, r], [z[idx], z[idx]],
                    color='k', alpha=0.8, linewidth=component_lw+2, zorder=998)
            idx += 1

        elif component.type == 'Lens':
            ax.text(label_x, component.z-0.01,
                    component.name, fontsize=label_fontsize, zorder = 1000)
            ax.add_patch(mpl.patches.Arc((0, component.z), component.radius*2, height=0.05,
                                         theta1=0, theta2=180, linewidth=1, fill=False, zorder=-1, edgecolor='k'))
            ax.add_patch(mpl.patches.Arc((0, component.z), component.radius*2, height=0.05,
                                         theta1=180, theta2=0, linewidth=1, fill=False, zorder=999, edgecolor='k'))

            idx += 1

        elif component.type == 'Astigmatic Lens':
            ax.text(label_x, component.z-0.01,
                    component.name, fontsize=label_fontsize, zorder = 1000)
            ax.add_patch(mpl.patches.Arc((0, component.z), component.radius*2, height=0.05,
                                         theta1=0, theta2=180, linewidth=1, fill=False, zorder=-1, edgecolor='k'))
            ax.add_patch(mpl.patches.Arc((0, component.z), component.radius*2, height=0.05,
                                         theta1=180, theta2=0, linewidth=1, fill=False, zorder=999, edgecolor='k'))

            idx += 1
        elif component.type == 'Deflector':
            r = component.radius
            ax.text(label_x, component.z-0.01,
                    component.name, fontsize=label_fontsize, zorder = 1000)
            ax.plot([-r, 0], [z[idx], z[idx]],
                    color='lightcoral', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([0, r], [z[idx], z[idx]],
                    color='lightblue', alpha=1, linewidth=component_lw, zorder=999)
            ax.plot([-r, r], [z[idx], z[idx]],
                    color='k', alpha=0.8, linewidth=component_lw+2, zorder=998)

            idx += 1
        elif component.type == 'Sample':
            ax.text(label_x, component.z-0.01,
                    component.name, fontsize=label_fontsize, zorder = 1000)
            w = component.width
            ax.plot([component.x-w/2, component.x+w/2], [z[idx], z[idx]],
                    color='dimgrey', alpha=0.8, linewidth=3)

            idx += 1

        allowed_rays = list(set(allowed_rays).difference(
            set(component.blocked_ray_idcs)))
        allowed_rays.sort()

        if len(allowed_rays) > 0:
            edge_rays = [allowed_rays[0], allowed_rays[-1]]
            new_edges = np.where(np.diff(allowed_rays) != 1)[0].tolist()

            for new_edge in new_edges:
                edge_rays.extend(
                    [allowed_rays[new_edge], allowed_rays[new_edge+1]])

            edge_rays.sort()

        else:
            break
        
    #We need to repeat the code once more for the rays at the end
    if allowed_rays != []:
        if highlight_edges == True:
            ax.plot(x[idx-1:idx+1, edge_rays], z[idx-1:idx+1],
                    color='k', linewidth=edge_lw, alpha=1, zorder=2)
        if fill_between == True:
            pair_idx = 0
            for first, second in zip(edge_rays[::2], edge_rays[1::2]):
                if len(edge_rays) == 4:
                    ax.fill_betweenx(z[idx-1:idx+1], x[idx-1:idx+1, first], x[idx-1:idx+1, second],
                                     color=fill_color_pair[pair_idx], edgecolor=fill_color_pair[pair_idx], alpha=fill_alpha, zorder=1)
                    pair_idx += 1
                else:
                    ax.fill_betweenx(z[idx-1:idx+1], x[idx-1:idx+1, first], x[idx-1:idx+1, second],
                                     color=fill_color, edgecolor=fill_color, alpha=fill_alpha, zorder=0)
        if plot_rays == True:
            ax.plot(x[idx-1:idx+1, allowed_rays], z[idx-1:idx+1],
                    color=ray_color, linewidth=ray_lw, alpha=ray_alpha, zorder=1)
    
    #Create the final labels and plot the detector shape
    ax.text(label_x, -0.01, 'Detector', fontsize=label_fontsize, zorder = 1000)
    ax.plot([-model.detector_size/2, model.detector_size/2],
            [0, 0], color='dimgrey', alpha=1, linewidth=component_lw)
    
    return fig, ax


components = [
	#comp.Lens(name = 'Electrostatic Lens', z = 0.95, f = -0.05),
	comp.Lens(name = 'Condenser Lens', z = 0.8, f = -0.075),
	comp.Sample(z = 0.68, name='sample', label_radius=0.3, width=0.15, num_points=50,x = 0., y = 0.),
	comp.Lens(name = 'Objective Lens', z = 0.6, f = -0.055),
	comp.Lens(name = 'Projector Lens', z = 0.2, f = -0.11),
	]

model_ = Model(components, beam_z=1, beam_type='x_axial',
                   num_rays=32, gun_beam_semi_angle=0.25)

name = 'electronoptics_model_tem_recoloured.svg'
fig, ax = show_matplotlib(model_, name = name, label_fontsize = 14)
fig.suptitle('TEM basic ElectronOptics Model', fontsize=32)
fig.savefig(name, dpi = 500)
