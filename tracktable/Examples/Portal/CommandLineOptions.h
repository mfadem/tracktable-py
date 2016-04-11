/*
 * Copyright (c) 2015, Sandia Corporation.  All rights
 * reserved.
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

#ifndef _CommandLineOptions_h
#define _CommandLineOptions_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>

typedef tracktable::string_type string_type;
typedef tracktable::string_vector_type string_vector_type;
typedef std::pair<string_type, std::size_t> field_assignment_type;

struct CommandLineOptions
{
  string_type InputFilename;
  string_type OutputDirectory;
  string_type OutputFilename;
  string_type Domain;
  string_type FieldDelimiter;
  double      SeparationDistance;
  double      SeparationSeconds;
  double      PortalSeparation;
  std::size_t Depth;
  std::size_t BinSize;
  std::size_t MinVal;
  std::size_t ObjectIdColumn;
  std::size_t TimestampColumn;
  std::size_t FirstCoordinateColumn;
  std::size_t SecondCoordinateColumn;
  std::size_t MinimumNumPoints;
  std::vector<field_assignment_type> RealFields;
  std::vector<field_assignment_type> IntegerFields;
  std::vector<field_assignment_type> TimestampFields;
  std::vector<field_assignment_type> StringFields;
};

#endif
