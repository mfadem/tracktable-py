#
# Copyright (c) 2014-2022 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
tracktable.render.render_trajectories - render trajectories in python

This is a set of function that intend to allow user-friendly rendering
of trajectories. A user should be able to simply use the function
render_trajectories(trajs) passing a single parameter that is a list
of trajectories and get a rendering of those trajectories, whether
running as an interactive map inside of a noetbook or from the command
line and saved as a static image to a file.

In addition render_trajectories supports many parameters to enable
specifying a myriad of options for rendering the trajectories,
including allowing users to explicitly specify the rendering backend.
"""
import logging

from tracktable.core.geomath import simplify
from tracktable.render.backends import bokeh_backend, cartopy_backend, folium_backend, ipyleaflet_backend
from tracktable.render.map_processing import common_processing

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------

def render_trajectories(trajectories, backend='', simplify_traj=False, simplify_tol=0.0001, **kwargs):
    """Render a list of trajectories interactively or as a static image

    This function will render a list of trajectories using Folium (for
    interactive display) if you are in a Jupyter notebook or using Cartopy
    (for a static image) if you are running from a script.

    Args:
        trajectories (single Tracktable trajectory or list of trajectories):
            Trajectories to render

    Keyword Arguments:
        backend (str): Which back end to use.  This can be 'folium' to force
            Folium interactive rendering or 'cartopy' to force static images.
            Defaults to None, which lets the renderer select automatically.
        simplify_traj (bool): Simplify trajectories prior to rendering them
        simplify_tol (float): Tolerance to use when simplifying trajectories,
            default is 0.0001
        map_canvas (map object for given backend): rather than create a new
            map, append to this given map
        obj_ids (str or list of str): only display trajecteories
            whose object id matches the given string or a string from
            the given list of strings.
        map_bbox ([minLon, minLat, maxLon, maxLat]): bounding box for
            custom map extent. By default automatically set to
            make all trajectories visible.
        show_lines (bool): whether or not to show the line segments
            of the trajecotry (Default: True)
        gradient_hue (float or list of floats): hue or list of hues
            (one per trajectory) to be used in definig the gradient color
            map (dark to light) for the trajectories. Only used if
            line_color and color_map are not used (set to '').
            If line_color, color_map and gradient_hue are all unset the
            default behavior is to set the gradient_hue based on a hash
            of the object_id
        color_map (name of standard colormap as string or matplotlib
            color_map object or list of either): The color map to use
            in rendering the segments of each trajectory. Overrides the
            gradient_hue value. Can be a list of color map objects or
            a list of matplotlib color map name strings the same length
            the length of the list of trajectories. Only used if
            line_color is not used (set to '').
        line_color (name of standard color as string, hex color string
            or matplotlib color object, or list of any of these): The
            single color to use for all the segments in each trajectory.
            Overrides color_map and gradient_hue values. Can be a list
            of matplotlib color name strings, hex color strings or
            matplotlib color objects the same length as the length of
            the list of trajectories.
        linewidth (float): Width of the trajectory segments.
            (Default: folium 2.5, cartopy 2)
        show_points (bool): whether or not to show the points along
            the trajecotry (Default: False)
        point_size (float): radius of the points along the path
            (Default: folium 0.6, cartopy 10.0)
        point_color = (name of standard color as string, hex color string
            or matplotlib color object, or list of any of these): The
            single color to use for all the points in each trajectory.
            Can be a list of matplotlib color name strings, hex color
            strings or matplotlib color objects the same length as the
            length of the list of trajectories. If not specified, the
            color matches the segment incident at the point.
        dot_size (float): radius of a dot drawn at the latest point of
            each trajectory (Default: folium 0.7, cartopy 10.0)
        dot_color (name of standard color as string, hex color string or
            matplotlib color object): Color of spot that will be drawn at
            the latest point of each trajecctory (Default: 'white')
        trajectory_scalar_generator (function): Function to generate
            scalars for a trajectory
            (Default: path_length_fraction_generator)
        trajectory_linewidth_generator (function): Function to generate
            path widths for a trajectory (Default: None)
        color_scale (matplotlib.colors.Normalize() or LogNorm()): Linear or logarithmic scale
            (Default: matplotlib.colors.Normalize(vmin=0, vmax=1))
        show (bool): whether or not to show the result (if possible)
            (default True) if saving to a file, might not want to view.
        save (bool): whether or not to save the result to a file.
            For folium the results can be saved to an html file. For
            cartopy the results can be saved as an image. If no filename
            is given, a default filename including the timestamp is used.
            (default False)
        filename (str): Path and filename to save the results to, if
            save is set to True. If no filename is given, a default
            filename including the timestamp is used.
        map_projection (Cartopy CRS): Cartopy CRS projection object (optional), used for Cartopy rendering only. (Default: None)
        transform: Matplotlib axes to render into, used for Cartopy rendering only. (Default: cartopy.crs.PlateCarree())
        tiles (str): Map tiles to use during image generation, the name
            or server url can be used. Options include OpenStreetMaps,
            StamenTerrain, StamenToner, StamenWatercolor, CartoDBPositron
            CartoDBDark_Matter, used for Folium rendering only. (Default: 'cartodbdark_matter')
        attr (str): Map tile attribution; only required if passing custom tile URL,
            used for Folium rendering only. (Default: ".")
        crs (str): Defines coordinate reference systems for projecting geographical
            points into pixel (screen) coordinates and back,
            used for Folium rendering only. (Default: "EPSG3857")
        point_popup_properties (list): Point properties, used for Folium rendering only.
        show_distance_geometry (bool): Boolean to enable displaying distance geometry for a given
            trajectory, used for Folium rendering only. (Default: False)
        distance_geometry_depth (int): Level of distance geometry to display, used for Folium rendering only. (Default: 4)
        show_scale (bool): Boolean to draw the distance scale of the map, used for Folium rendering only. (Default: True)
        max_zoom (int): Maximum allowed zoom level for the tile layer that is created, used for Folium rendering only. (Default: 22)
        fast (bool): Bool for reduced/faster processing of the folium map, used for Folium rendering only. (Default: False)

    """

    render_function = folium_backend.render_trajectories

    if backend == 'folium':
        render_function = folium_backend.render_trajectories
    elif backend == 'cartopy':
        render_function = cartopy_backend.render_trajectories
    elif backend == 'ipyleaflet': # currently experimental
        logger.warn("ipyleaflet trajectory rendering backend is currently experimental, proceed with caution.")
        render_function = ipyleaflet_backend.render_trajectories
    elif backend == 'bokeh':  # currently experimental
        logger.warn("Bokeh trajectory rendering backend is currently experimental, proceed with caution.")
        render_function = bokeh_backend.render_trajectories
    else:
        if backend != '':
            logger.error("Error: Invalid backend specified in",
                  "render_trajectories.",
                  "Valid backends include: folium, and cartopy",
                  "Defauting to folium backend")
        if common_processing.in_notebook():
            if type(trajectories) is not list or len(trajectories) <= 10000:
                render_function = folium_backend.render_trajectories
            else:
                logger.warn("Too many trajectories to plot with folium. Reverting to non-interactive backend. Override with backend='folium'")
                render_function = cartopy_backend.render_trajectories
        else:
            render_function = cartopy_backend.render_trajectories

    if simplify_traj:
        if type(trajectories) is not list:
            trajectories = simplify(trajectories, simplify_tol)
        else:
            for index, traj in enumerate(trajectories):
                trajectories[index] = simplify(traj, simplify_tol)

    return render_function(trajectories, **kwargs)

# ----------------------------------------------------------------------

#todo should this return anything?
def render_trajectories_separate(trajectories, backend='', **kwargs):
    """Render a list of trajectories such that each trajectory is
    rendered separately in its own map. See render_trajectories for
    parameters

    Args:
        trajectories (Tracktable trajectory or list of trajectory objects):
            List of trajectories to render

    Keyword Args:
        backend (str): The backend to use for rendering default is folium if in a notebook and cartopy otherwise.
        kwargs (dict): Additional parameters to customize the rendered trajectory

    Returns:
        No return value

    """

    for traj in trajectories:
        render_trajectories(traj, backend=backend, show=True, **kwargs)

# ----------------------------------------------------------------------

def render_trajectory(trajectory, backend='', **kwargs):
    """Render a single trajectory
    This function allows users to render a single trajectory, and just
    calls render_trajectories, which also handles single trajectories.

    Arguments:
        trajectory (Trajectory): The trajectory object to render

    Keyword Arguments:
        backend (str): the rendering backend (cartopy, folium, etc)
            default is folium if in a notebook and cartopy otherwise.
        kwargs (dict): see render_trajectories for other arguments

    Returns:
        No return value

    """

    render_trajectories(trajectory, backend, **kwargs)

# ----------------------------------------------------------------------

def render_trajectories_for_print(trajectories, filename,
                                  land_fill_color='white',
                                  water_fill_color='#EEEEEE',
                                  color_map='viridis',
                                  dot_color='grey',
                                  linewidth=1.5,
                                  figsize=(6,4),
                                  save=True,
                                  **kwargs):
    """Render a list of trajectories with print-friendly defaults

    This function will render a list of trajectories using Cartopy
    in a way this is more appropriate for use in printed media.
    """

    if not 'gradient_hue' in kwargs:
        kwargs['color_map']=color_map  #make this the default, but let it be supersceded by gradient_hue

    render_trajectories(trajectories, backend='cartopy', land_fill_color=land_fill_color,
                                water_fill_color=water_fill_color, dot_color=dot_color,
                                linewidth=linewidth, figsize=figsize, save=save,
                                filename=filename, **kwargs)

# ----------------------------------------------------------------------

def render_trajectories_for_print_using_tiles(trajectories, filename,
                                              color_map='viridis',
                                              dot_color='grey', linewidth=1.5,
                                              figsize=(6,4),
                                              save=True,
                                              tiles='https://basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png',
                                              fill_land=False,
                                              fill_water=False,
                                              draw_coastlines=False,
                                              draw_countries=False,
                                              draw_states=False,
                                              **kwargs):
    """Render a list of trajectories with print-friendly defaults
       but using tiles as the basemap.

    This function will render a list of trajectories using Cartopy
    in a way this is more appropriate for use in printed media.
    """

    if not 'gradient_hue' in kwargs:
        kwargs['color_map']=color_map  #make this the default, but let it be supersceded by gradient_hue

    render_trajectories(trajectories, backend='cartopy', dot_color=dot_color, linewidth=linewidth,
                                figsize=figsize, save=save, filename=filename,
                                tiles=tiles, fill_land=fill_land, fill_water=fill_water,
                                draw_coastlines=draw_coastlines, draw_countries=draw_countries,
                                draw_states=draw_states, **kwargs)
