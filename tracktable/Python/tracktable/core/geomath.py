#
# Copyright (c) 2014-2017 National Technology and Engineering
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
This file contains useful math functions.  Some of them will be
related to geography such as 'find the distance between these two
points on the globe'.
"""

from __future__ import division, print_function, absolute_import
from six.moves import range


import math
import sys


from ._domain_algorithm_overloads import distance as _distance
from ._domain_algorithm_overloads import bearing as _bearing
from ._domain_algorithm_overloads import interpolate as _interpolate
from ._domain_algorithm_overloads import signed_turn_angle as _signed_turn_angle
from ._domain_algorithm_overloads import unsigned_turn_angle as _unsigned_turn_angle
from ._domain_algorithm_overloads import speed_between as _speed_between
from ._domain_algorithm_overloads import point_at_fraction as _point_at_fraction
from ._domain_algorithm_overloads import point_at_time as _point_at_time
from ._domain_algorithm_overloads import subset_during_interval as _subset_during_interval
from ._domain_algorithm_overloads import length as _length
from ._domain_algorithm_overloads import end_to_end_distance as _end_to_end_distance
from ._domain_algorithm_overloads import intersects as _intersects
from ._domain_algorithm_overloads import geometric_median as _geometric_median
from ._domain_algorithm_overloads import geometric_mean as _geometric_mean
from ._domain_algorithm_overloads import simplify as _simplify
from ._domain_algorithm_overloads import convex_hull_perimeter as _convex_hull_perimeter
from ._domain_algorithm_overloads import convex_hull_area as _convex_hull_area
from ._domain_algorithm_overloads import convex_hull_aspect_ratio as _convex_hull_aspect_ratio

def xcoord(thing):
    """Return what we think is the X-coordinate for an object.

    If the supplied thing has a property named 'x' then we return
    that.  Otherwise we try to return its first element.

    Args:
       point: Object with an 'x' property or tuple of numbers

    Returns:
       Number corresponding to x coordinate

    Raises:
       AttributeError if attempt at access fails
    """

    try:
        return thing.x
    except AttributeError:
        return thing[0]

def ycoord(thing):
    """Return what we think is the Y-coordinate for an object.

    If the supplied thing has a property named 'y' then we return
    that.  Otherwise we try to return its second element.

    Args:
       point: Object with an 'y' property or tuple of numbers

    Returns:
       Number corresponding to y coordinate

    Raises:
       AttributeError if attempt at access fails
    """

    try:
        return thing.y
    except AttributeError:
        return thing[1]

def longitude(thing):
    """Return the longitude from a point or tuple

    It is often convenient to specify a point as a (lon, lat) tuple
    instead of a fullfledged TrajectoryPoint.  By using this function
    to look up longitude we can cope gracefully with both.

    Args:
       point: TrajectoryPoint or (lon, lat) tuple

    Returns:
       Longitude as float

    Raises:
       AttributeError: if attempt at access fails
    """

    if hasattr(thing, 'longitude'):
        return thing.longitude
    else:
        return thing[0]

def latitude(thing):
    """Return the latitude from a point or tuple

    It is often convenient to specify a point as a (lon, lat) tuple
    instead of a fullfledged TrajectoryPoint.  By using this function
    to look up latitude we can cope gracefully with both.

    Args:
       point: TrajectoryPoint or (lon, lat) tuple

    Returns:
       Latitude as float

    Raises:
       AttributeError: if attempt at access fails
    """

    if hasattr(thing, 'latitude'):
        return thing.latitude
    else:
        return thing[1]


def longitude_or_x(thing):
    """Return the longitude or X-coordinate from a point or tuple

    Args:
       point: TrajectoryPoint or (lon, lat) tuple or (x, y) point

    Returns:
       Longitude/X as float

    Raises:
       AttributeError: if attempt at access fails
    """

    if hasattr(thing, 'longitude'):
        return thing.longitude
    elif hasattr(thing, 'x'):
        return thing.x
    else:
        return thing[0]

def latitude_or_y(thing):
    """Return the latitude or Y-coordinate from a point or tuple

    Args:
       point: TrajectoryPoint or (lon, lat) tuple or (x, y) point

    Returns:
       Latitude/Y as float

    Raises:
       AttributeError: if attempt at access fails
    """

    if hasattr(thing, 'latitude'):
        return thing.latitude
    elif hasattr(thing, 'y'):
        return thing.y
    else:
        return thing[1]

def altitude(thing):
    """Return the altitude from a point or tuple

    It is often convenient to specify a point as a (lon, lat,
    altitude) tuple instead of a full-fledged TrajectoryPoint.  By
    using this function to look up altitude we can cope gracefully
    with both.

    Args:
       point: TrajectoryPoint or (lon, lat, altitude) tuple

    Returns:
       Altitude as float

    Raises:
       AttributeError: if attempt at access fails
    """
    if hasattr(thing, 'altitude'):
        return thing.altitude
    else:
        try:
            return thing.properties['altitude']
        except IndexError:
            return 0

def almost_equal(a, b, relative_tolerance=1e-6):
    """Check two numbers for equality within a tolerance

    Arguments:
       a (float): First number
       b (float): Second number
       relative_tolerance (float): Numbers must be close to within this fraction of their average to be considered equal

    Returns:
       True/false depending on whether or not they're equal-ish
    """

    return ( math.fabs(a - b) < relative_tolerance * 0.5 * ( math.fabs(a) + math.fabs(b) ) )

# ----------------------------------------------------------------------

def bearing(origin, destination):
    """Compute angular bearing between two points

    Source: http://gagravarr.livejournal.com/109998.html with modifications.

    Args:
       origin (BasePoint or TrajectoryPoint): start point
       destination (BasePoint or TrajectoryPoint): end point

    Returns:
       Bearing from origin to destination.

    Domain Information:

       Terrestrial: Returned in degrees.  0 is due north, 90 is due
       east.

       Cartesian2D: Returned in radians.  0 is positive X, pi/2 is
       positive Y.

       Cartesian3D: Not defined.
    """


    return _bearing(origin, destination)

# ----------------------------------------------------------------------

def speed_between(point1, point2):
    """Return speed in km/hr between two timestamped points.

    Args:
      point1 (TrajectoryPoint): Start point
      point2 (TrajectoryPoint): End point

    Returns:
      Speed (as a float) measured in domain-specific units

    Domain Info:
      Terrestrial: Speed is in km/hr
      Cartesian2D: Speed is in units/sec
      Cartesian3D: Speed is in units/sec
    """

    return _speed_between(point1, point2)


# ----------------------------------------------------------------------

def signed_turn_angle(a, b, c):
    """Return signed turn angle between (a, b) and (b, c).

    The magnitude of the angle tells you how far you turned.  The sign
    of the angle tells you whether you turned right or left.  Which
    one depends on the domain.

    Args:
      a (BasePoint): first point
      b (BasePoint): second point
      c (BasePoint): third point

    Returns:
      Signed angle in domain-dependent units

    Domain:
      Terrestrial: angle in degrees, positive angles are clockwise
      Cartesian2D: angle in radians, positive angles are counterclockwise
      Cartesian3D: not defined
    """

    return _signed_turn_angle(a, b, c)

# ----------------------------------------------------------------------

def unsigned_turn_angle(a, b, c):
    """Return unsigned turn angle between (a, b) and (b, c).

    The magnitude of the angle tells you how far you turned.  This
    function will not tell you whether you turned right or left - for
    that you need signed_turn_angle.

    Args:
      a (BasePoint): first point
      b (BasePoint): second point
      c (BasePoint): third point

    Returns:
      Angle in domain-dependent units

    Domain:
      Terrestrial: angle in degrees between 0 and 180
      Cartesian2D: angle in radians between 0 and pi
      Cartesian3D: angle in radians between 0 and pi

    """

    return _unsigned_turn_angle(a, b, c)

# ----------------------------------------------------------------------

def intersects(thing1, thing2):
    """Check to see whether two geometries intersect

    The geometries in question must be from the same domain.  They can
    be points, trajectories, linestrings or bounding boxes.

    Args:
      thing1: Geometry object
      thing2: Geometry object

    Returns:
      True or False
    """

    return _intersects(thing1, thing2)

# ----------------------------------------------------------------------

def length(trajectory):

    """Return the length of a path in domain-dependent units

    This is the total length of all segments in the trajectory.

    Args:
      trajectory (Trajectory): Path whose length we want

    Returns:
      Length in domain-dependent units

    Domain:
      Terrestrial: distance in km
      Cartesian2D: distance in units
      Cartesian3D: distance in units
    """

    return _length(trajectory)

# ----------------------------------------------------------------------

def end_to_end_distance(trajectory):
    """Return the distance between a path's endpoints

    This is just the distance between start and end points rather than
    the total distance traveled.

    Args:
      trajectory (Trajectory): Path whose length we want

    Returns:
      Length in domain-dependent units

    Domain:
      Terrestrial: distance in km
      Cartesian2D: distance in units
      Cartesian3D: distance in units

    """

    return _end_to_end_distance(trajectory)

# ----------------------------------------------------------------------

def point_at_fraction(trajectory, fraction):
    """Return a point from a trajectory at a specific fraction of its distance

    This function will estimate a point at a trajectory at some
    specific fraction of its total travel distance.  If the supplied
    fraction does not fall exactly on a vertex of the trajectory we
    will interpolate between the nearest two points.

    Fractions before the beginning or after the end of the trajectory
    will return the start and end points, respectively.

    Args:
      trajectory (Trajectory): Path to sample
      fraction (float): Value between 0 and 1.  0 is the beginning and 1 is the end.

    Returns:
      TrajectoryPoint at specified fraction

    """

    return _point_at_fraction(trajectory, fraction)


# ----------------------------------------------------------------------

def point_at_time(trajectory, when):
    """Return a point from a trajectory at a specific time

    This function will estimate a point at a trajectory at some
    specific time.  If the supplied timestamp does not fall exactly on
    a vertex of the trajectory we will interpolate between the nearest
    two points.

    Times before the beginning or after the end of the trajectory will
    return the start and end points, respectively.

    Args:
      trajectory (Trajectory): Path to sample
      when (datetime): Timestamp for which we want the point

    Returns:
      TrajectoryPoint at specified time

    """

    return _point_at_time(trajectory, when)

# ----------------------------------------------------------------------

def subset_during_interval(trajectory, start_time, end_time):
    """Return a subset of a trajectory between two times

    This function will extract some (possibly empty) subset of a
    trajectory between two timestamps.

    If the time interval is entirely outside the trajectory, the
    result will be an empty trajectory.  Otherwise we will use
    point_at_time to find the two endpoints and build a new trajectory
    from the endpoints and all trajectory points between them.

    Args:
      trajectory (Trajectory): Path to sample
      start_time (datetime): Timestamp for beginning of subset
      end_time (datetime): Timestamp for end of subset

    Returns:
      Trajectory for desired interval

    """

    return _subset_during_interval(trajectory, start_time, end_time)

# ----------------------------------------------------------------------

def distance(hither, yon):
    """Return the distance between two points

    This function will compute the distance between two points in
    domain-specific units.

    The points being measured must be from the same domain.

    Args:
      hither (BasePoint): point 1
      yon (BasePoint): point 2

    Returns:
      Distance between hither and yon

    Domain:
      Terrestrial domain returns distance in km.
      Cartesian domains return distance in native units.
    """

    return _distance(hither, yon)

# ----------------------------------------------------------------------

def interpolate(start, end, t):
    """Interpolate between two points

    This function will interpolate linearly between two points.  It is
    aware of the underlying coordinate system: interpolation on the
    globe will be done along great circles and interpolation in
    Cartesian space will be done along a straight line.

    The points being measured must be from the same domain.

    Args:
      start (BasePoint or TrajectoryPoint): point 1
      end (BasePoint or TrajectoryPoint): point 2
      t (float in [0, 1]): interpolant

    Returns:
      New point interpolated between start and end
    """

    return _interpolate(start, end, t)

# ----------------------------------------------------------------------

def sanity_check_distance_less_than(max_distance):
    def sanity_check(point1, point2):
        return ( distance(point1, point2) < max_distance )

    return sanity_check

# ----------------------------------------------------------------------

def compute_bounding_box(point_sequence):
    """Compute a bounding box for a sequence of points.

    This function will construct a domain-specific bounding box over
    an arbitrary sequence of points.  Those points must all have the
    same type.

    Args:
      point_sequence: Iterable of points

    Returns:
      Bounding box with min_corner, max_corner attributes

    Domain:
      Each domain returns a separate bounding box type.
    """

    min_corner = None
    max_corner = None
    bbox_type = None

    num_points = 0
    
    for point in point_sequence:
        num_points += 1
        if bbox_type is None:
            bbox_type = point.domain_classes['BoundingBox']

        if min_corner is None:
            min_corner = point.domain_classes['BasePoint']()
            max_corner = point.domain_classes['BasePoint']()
            for i in range(len(point)):
                min_corner[i] = point[i]
                max_corner[i] = point[i]
        else:
            for i in range(len(point)):
                min_corner[i] = min(min_corner[i], point[i])
                max_corner[i] = max(max_corner[i], point[i])

    if num_points == 0:
        print("ERROR: Cannot compute bounding box.  No points provided.")
        return None
    else:
        print("Bounding box points: {}, {}".format(min_corner, max_corner))
        result = bbox_type(min_corner, max_corner)
        print("Final bounding box: {}".format(result))
        return result


# ----------------------------------------------------------------------

def recompute_speed(trajectory, target_attribute_name="speed"):
    """Use points and timestamps to compute speed

    The speed data in trajectories is often suspect.  This method goes
    through and recomputes it based on the distance between
    neighboring points and the time elapsed between those points.

    The speed at point N is computed using the distance and time since
    point N-1.  The speed at point 0 is copied from point 1.

    Args:
      trajectory: Any Tracktable trajectory
      target_attribute_name: Speed will be stored in this property at 
          each point.  Defaults to 'speed'.

    The trajectory will be modified in place instead of returning a
    new copy.
    """

    if len(trajectory) == 0:
        return
    elif len(trajectory) == 1:
        trajectory[0].properties[target_attribute_name] = 0
    else:
        for point_index in range(1, len(trajectory)):
            trajectory[point_index].properties[target_attribute_name] = speed_between(
                trajectory[point_index - 1],
                trajectory[point_index]
            )

        trajectory[0].properties[target_attribute_name] = trajectory[1].properties[target_attribute_name]

# ----------------------------------------------------------------------

def geometric_median(points):
    """Compute L1 multivariate median of points

    The multivariate median generalizes the standard 1D median to two
    or more dimensions.

    Args:
       points: Iterable of points for which you want a median

    Returns:
       Single point of the same type that came in
    """

    my_points = list(points)
    if len(my_points) == 0:
        return None
    return _geometric_median(my_points[0], my_points)



# ----------------------------------------------------------------------

def geometric_mean(points):
    """Compute mean of input points

    This is the regular mean: just the component-wise average of the
    coordinates.

    NOTE: This does not yet do the right thing with terrestrial
    points.  It should normalize their coordinates to make sure they
    do not fall across the limb of the map before taking the average.

    Args:
       points: Sequence of points for which you want a mean

    Returns:
       Single point of the same type that came in

    """

    my_points = list(points)
    if len(my_points) == 0:
        return None
    return _geometric_mean(my_points[0], my_points)

# ----------------------------------------------------------------------

def simplify(trajectory, tolerance):
    """Geometric simplification for trajectory

    This function reduces the number of points in a trajectory without
    introducing positional error greater than the supplied tolerance.
    Under the hood it uses Douglas-Peucker simplification.

    NOTE: The points in the output are copies of the points in the
    input.  Changing the input after a call to simplify() will have no
    effect on previous results.

    NOTE: This function only cares about geometric error in the
    trajectory.  It does not account for error in the attributes
    attached to each point.

    Args:
       trajectory: Trajectory to simplify
       tolerance:  Error tolerance measured in the trajectory's native distance

    Returns:
       Simplified version of trajectory

    """

    return _simplify(trajectory, tolerance)

# ----------------------------------------------------------------------

def convex_hull_perimeter(trajectory):
    """Compute the perimeter of the convex hull of a trajectory

    Perimeter length will be returned in the native distance units of
    the domain.  This is kilometers for the terrestrial domain and
    untyped units for Cartesian.

    Args:
      trajectory: Trajectory whose hull you want to measure

    Returns:
      Perimeter of the trajectory's convex hull
    """

    return _convex_hull_perimeter(trajectory)


# ----------------------------------------------------------------------

def convex_hull_area(trajectory):
    """Compute the area of the convex hull of a trajectory

    Area will be returned in the native area units of
    the domain.  This is square kilometers for the terrestrial domain and
    untyped squared units for Cartesian.

    Args:
      trajectory: Trajectory whose hull you want to measure

    Returns:
      Area of the trajectory's convex hull
    """

    return _convex_hull_area(trajectory)


# ----------------------------------------------------------------------

def convex_hull_aspect_ratio(trajectory):
    """Compute the aspect ratio of the convex hull of a trajectory

    Aspect ratio is a dimensionless number.  It refers to the ratio of
    the shortest axis of the polygon over the longest.

    Note that we compute an approximation using the vertices of the
    convex hull.  This will get better in a future release.

    Args:
      trajectory: Trajectory whose shape you want to measure

    Returns:
      Aspect ratioof the trajectory's convex hull

    """

    return _convex_hull_aspect_ratio(trajectory)