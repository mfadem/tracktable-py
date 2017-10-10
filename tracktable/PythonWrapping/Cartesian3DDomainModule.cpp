/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


// Tracktable Trajectory Library
//
// Boost.Python wrappers for the Cartesian3D domain types
//
// This module ONLY includes the classes (points, trajectory and
// reader) exposed by the 3D cartesian domain.  All of the algorithm
// overloads are exposed in AlgorithmOverloadsModule so that
// Boost.Python can sort out the C++ overloading by itself.

#include <boost/python.hpp>
#include <boost/python/class.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/return_internal_reference.hpp>
#include <Python.h>

#include <tracktable/Domain/Cartesian3D.h>
#include <tracktable/Core/Timestamp.h>

#include <tracktable/IO/PointWriter.h>
#include <tracktable/IO/TrajectoryWriter.h>

#include <tracktable/PythonWrapping/PythonFileLikeObjectStreams.h>
#include <tracktable/PythonWrapping/DomainWrapperTemplates.h>
#include <tracktable/PythonWrapping/PythonAwarePointReader.h>
#include <tracktable/PythonWrapping/PythonAwareTrajectoryReader.h>
#include <tracktable/PythonWrapping/PythonTypedObjectWriter.h>

//#include <tracktable/PythonWrapping/PickleTrajectoryPoints.h>

//#include <tracktable/PythonWrapping/PickleTrajectories.h>


using tracktable::domain::cartesian3d::base_point_type;
using tracktable::domain::cartesian3d::trajectory_point_type;
using tracktable::domain::cartesian3d::trajectory_type;
using tracktable::domain::cartesian3d::base_point_reader_type;
using tracktable::domain::cartesian3d::trajectory_point_reader_type;
using tracktable::domain::cartesian3d::trajectory_reader_type;
using tracktable::domain::cartesian3d::box_type;

// ----------------------------------------------------------------------


namespace {

// ----------------------------------------------------------------------

void set_min_corner(box_type& box, base_point_type const& corner)
{
  box.min_corner() = corner;
}

void set_max_corner(box_type& box, base_point_type const& corner)
{
  box.max_corner() = corner;
}

base_point_type min_corner(box_type const& box)
{
  return box.min_corner();
}

base_point_type max_corner(box_type const& box)
{
  return box.max_corner();
}

}


// ----------------------------------------------------------------------

#if 0
std::ostream&
operator<<(std::ostream& out, base_point_type const& point)
{
  out << point.to_string();
  return out;
}

std::ostream&
operator<<(std::ostream& out, trajectory_point_type const& point)
{
  out << point.to_string();
  return out;
}
#endif

std::ostream&
operator<<(std::ostream& out, box_type const& box)
{
  std::ostringstream outbuf;
  outbuf << "<BoundingBox: "
         << box.min_corner() << " - " << box.max_corner() << ">";
  out << outbuf.str();
  return out;
}

// ----------------------------------------------------------------------

void install_cartesian3d_box_wrappers()
{
  using namespace boost::python;
  class_<box_type>("BoundingBoxCartesian3D")
    .def("__init__", make_constructor(tracktable::python_wrapping::make_box<base_point_type, box_type>))
    .def("__init__", make_constructor(tracktable::python_wrapping::make_box<trajectory_point_type, box_type>))
//    .def(tracktable::python_wrapping::to_string_methods())
    .add_property("min_corner", ::min_corner, ::set_min_corner)
    .add_property("max_corner", ::max_corner, ::set_max_corner);
}

// ----------------------------------------------------------------------

void install_cartesian3d_base_point_wrappers()
{
  using namespace boost::python;
  using tracktable::python_wrapping::make_point_3d;

  class_< base_point_type >("BasePointCartesian3D")
    .def("__init__", make_constructor(make_point_3d<base_point_type>))
    .def(tracktable::python_wrapping::basic_point_methods())
    .def(tracktable::python_wrapping::point_to_string_methods())
    ;
}

// ----------------------------------------------------------------------

void install_cartesian3d_trajectory_point_wrappers()
{
  using namespace boost::python;
  using tracktable::python_wrapping::make_point_3d;

  class_< trajectory_point_type >("TrajectoryPointCartesian3D")
    .def("__init__", make_constructor( make_point_3d<trajectory_point_type> ))
    .def(tracktable::python_wrapping::basic_point_methods())
    .def(tracktable::python_wrapping::point_to_string_methods())
    .def(tracktable::python_wrapping::property_access_suite())
    .def(tracktable::python_wrapping::trajectory_point_methods())
    ;

}

// ----------------------------------------------------------------------

void install_point_reader_wrappers()
{
  using namespace boost::python;

  // TODO: Expose column_assignments and field_assignments the way I
  // expose the property map

  typedef tracktable::PythonAwarePointReader<base_point_reader_type> python_base_point_reader_type;
  typedef tracktable::PythonAwarePointReader<trajectory_point_reader_type> python_trajectory_point_reader_type;

  class_<python_base_point_reader_type>("BasePointReaderCartesian3D")
    .def(tracktable::python_wrapping::basic_point_reader_methods())
    .def(tracktable::python_wrapping::cartesian3d_point_reader_methods())
    ;

  class_<python_trajectory_point_reader_type>("TrajectoryPointReaderCartesian3D")
    .def(tracktable::python_wrapping::basic_point_reader_methods())
    .def(tracktable::python_wrapping::trajectory_point_reader_methods())
    .def(tracktable::python_wrapping::cartesian3d_point_reader_methods())
    ;

}

// ----------------------------------------------------------------------

void install_trajectory_reader_wrappers()
{
  using namespace boost::python;

  typedef tracktable::PythonAwareTrajectoryReader<trajectory_reader_type> python_trajectory_reader_type;

  class_<python_trajectory_reader_type>("TrajectoryReaderCartesian3D")
    .def(tracktable::python_wrapping::trajectory_reader_methods())
    ;
}

// ----------------------------------------------------------------------

void install_point_writer_wrappers()
{
  using namespace boost::python;

  typedef tracktable::PythonTypedObjectWriter<
    tracktable::PointWriter,
    tracktable::domain::cartesian3d::base_point_type
    > base_point_writer_t;

  typedef tracktable::PythonTypedObjectWriter<
    tracktable::PointWriter,
    tracktable::domain::cartesian3d::trajectory_point_type
    > trajectory_point_writer_t;

  class_< base_point_writer_t >("BasePointWriterCartesian3D")
    .def(tracktable::python_wrapping::common_writer_methods())
    .add_property("write_header",
                  &base_point_writer_t::write_header,
                  &base_point_writer_t::set_write_header)
    ;

  class_< trajectory_point_writer_t >("TrajectoryPointWriterCartesian3D")
    .def(tracktable::python_wrapping::common_writer_methods())
    .add_property("write_header",
                  &trajectory_point_writer_t::write_header,
                  &trajectory_point_writer_t::set_write_header)
    ;

}

// ----------------------------------------------------------------------

void install_trajectory_writer_wrappers()
{
  using namespace boost::python;

  typedef tracktable::PythonTypedObjectWriter<
    tracktable::TrajectoryWriter,
    tracktable::domain::cartesian3d::trajectory_type
    > trajectory_writer_t;

  class_< trajectory_writer_t >("TrajectoryWriterCartesian3D")
    .def(tracktable::python_wrapping::common_writer_methods())
    ;
}

// ----------------------------------------------------------------------

void install_cartesian3d_trajectory_wrappers()
{
  using namespace boost::python;

  class_< trajectory_type >("TrajectoryCartesian3D")
    .def(tracktable::python_wrapping::property_access_suite())
//    .def("from_position_list", &trajectory_from_position_list, return_value_policy<manage_new_object>())
    .def("__iter__", iterator<trajectory_type>())
    .def(self==self)
    .def(self!=self)
    .def(vector_indexing_suite<trajectory_type>())
    ;
}

// ----------------------------------------------------------------------

void install_cartesian3d_domain_wrappers()
{
  using namespace boost::python;

  install_cartesian3d_base_point_wrappers();
  install_cartesian3d_trajectory_point_wrappers();
  install_cartesian3d_trajectory_wrappers();
  install_point_reader_wrappers();
  install_trajectory_reader_wrappers();
  install_point_writer_wrappers();
  install_trajectory_writer_wrappers();
  install_cartesian3d_box_wrappers();
}

BOOST_PYTHON_MODULE(_cartesian3d)
{
  install_cartesian3d_domain_wrappers();
}