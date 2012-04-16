#ifndef _Network_h_
#define _Network_h_
/* Network.h
 *
 * Copyright (C) 2009-2012 Paul Boersma
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or (at
 * your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#include "Data.h"
#include "Graphics.h"

#include "Network_enums.h"

#include "Network_def.h"
oo_CLASS_CREATE (Network, Data);

Network Network_create (double minimumActivity, double maximumActivity, double spreadingRate,
	double selfExcitation, double minimumWeight, double maximumWeight, double learningRate, double leak,
	double xmin, double xmax, double ymin, double ymax, long numberOfNodes, long numberOfConnections);

Network Network_create_rectangle (double minimumActivity, double maximumActivity, double spreadingRate,
	double selfExcitation, double minimumWeight, double maximumWeight, double learningRate, double leak,
	long numberOfRows, long numberOfColumns, bool bottomRowClamped,
	double initialMinimumWeight, double initialMaximumWeight);
Network Network_create_rectangle_vertical (double minimumActivity, double maximumActivity, double spreadingRate,
	double selfExcitation, double minimumWeight, double maximumWeight, double learningRate, double leak,
	long numberOfRows, long numberOfColumns, bool bottomRowClamped,
	double initialMinimumWeight, double initialMaximumWeight);

/* End of file Network.h */
#endif
