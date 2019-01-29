/*********************************************
 * OPL 12.8.0.0 Model
 * Author: henry
 * Creation Date: Jan 25, 2019 at 3:48:57 PM
 *********************************************/

int MED1 = 7;
int MED2 = 2;
int MED3 = 4;

int MAX_DAY = 25;
int MAX_CONTAINER = 3;
int MAX_RANGE = MAX_DAY * (MED1 + MED2 + MED3);

range ITEM_RANGE = 1..MAX_RANGE;
range MED1_RANGE = 1 .. MAX_DAY*MED1;
range MED2_RANGE = MAX_DAY*MED1+1 .. MAX_DAY*(MED1+MED2);
range MED3_RANGE = MAX_DAY*(MED1+MED2)+1 .. MAX_DAY*(MED1+MED2+MED3);
range DRONE_RANGE = MAX_DAY*(MED1+MED2+MED3)+1 .. MAX_RANGE;

{string} Items = ...;
{string} Drones = ...;
{string} MEDs = ...;

int ExteriorWidth = ...;
int ExteriorHeight = ...;
int ExteriorLength = ...;
int InteriorWidth = ...;
int InteriorHeight = ...;
int InteriorLength = ...;
int DoorOpenWidth = ...;
int DoorOpenHeight = ...;

int Length[Items] = ...;
int Width[Items] = ...;
int Height[Items] = ...;
int Volume[Items] = ...;

dvar int+ item_is_type[ITEM_RANGE][Items];  // which type of item
dvar int+ container[ITEM_RANGE];            // which container

// 01 variables, left, under, back, container
dvar int+ l[ITEM_RANGE][ITEM_RANGE];
dvar int+ u[ITEM_RANGE][ITEM_RANGE];
dvar int+ b[ITEM_RANGE][ITEM_RANGE];
dvar int+ c[ITEM_RANGE][ITEM_RANGE];

// index variables, x, y, z
dvar float+ x[ITEM_RANGE];
dvar float+ y[ITEM_RANGE];
dvar float+ z[ITEM_RANGE];

// intermediate variables, length, width, height and volume
dvar float+ _l[ITEM_RANGE];
dvar float+ _w[ITEM_RANGE];
dvar float+ _h[ITEM_RANGE];
dvar float+ _v[ITEM_RANGE];

// intermediate variable, in container or not
dvar int+ _in_container[ITEM_RANGE];

// intermediate variable
dvar float+ _total_volume;


maximize _total_volume;


subject to {

// type is only
forall(i in ITEM_RANGE) {
  _in_container[i] == (sum(type in Items) item_is_type[i][type]);
  _in_container[i] <= 1;  // "<= 1" or "== 1" ?
  _in_container[i] >= 1 => (container[i] >= 1);
}

// intermediate results
forall(i in ITEM_RANGE) {
  _w[i] == (sum(type in Items) item_is_type[i][type] * Width[type]);
  _h[i] == (sum(type in Items) item_is_type[i][type] * Height[type]);
  _l[i] == (sum(type in Items) item_is_type[i][type] * Length[type]);
  _v[i] == (sum(type in Items) item_is_type[i][type] * Volume[type]);
}

// make sure items are "inside" the container
forall(i in ITEM_RANGE) {  
  x[i] <= InteriorWidth - _w[i];
  y[i] <= InteriorHeight - _h[i];
  z[i] <= InteriorLength - _l[i];
}

// relative position is only
forall(i in ITEM_RANGE) {
  forall(j in 1..i-1) {
    (container[i] >= 1 && container[j] >= 1) =>
    	  l[i][j] + l[j][i] + u[i][j] + u[j][i] + b[i][j] + b[j][i] + c[i][j] + c[j][i] == 1;
  }
}

// when c[i][j] == 1 or c[j][i] == 1 the items i, j are located in different bins
// when one of l[i][j], l[j][i], u[i][j], u[j][i], b[i][j], b[j][i] is equal to 1, 
//     items i and j are necessarily located in the same bin
forall(i in ITEM_RANGE) {
  forall(j in ITEM_RANGE) {
    (container[i] >= 1 && container[j] >= 1) =>
      (MAX_CONTAINER - 1) * (l[i][j] + l[j][i] + u[i][j] + u[j][i] + b[i][j] + b[j][i])
        + container[i] - container[j] + MAX_CONTAINER * c[i][j] <= MAX_CONTAINER - 1;
  }
}

// no overlap
forall(i in ITEM_RANGE) {
  forall(j in ITEM_RANGE) {
  	x[i] - x[j] + InteriorWidth * (l[i][j] - c[i][j] - c[j][i]) <= InteriorWidth - _w[i];
  	y[i] - y[j] + InteriorHeight * (u[i][j] - c[i][j] - c[j][i]) <= InteriorHeight - _h[i];
  	z[i] - z[j] + InteriorLength * (b[i][j] - c[i][j] - c[j][i]) <= InteriorLength - _l[i];
  }
}

// 01 variable constrains
forall(i in ITEM_RANGE) {
  forall(j in ITEM_RANGE) {
    l[i][j] <= 1;
    u[i][j] <= 1;
    b[i][j] <= 1;
    c[i][j] <= 1;
  }
}

object_function:
  _total_volume == (sum(i in ITEM_RANGE) _v[i]);

preknowledge:
  forall(i in MED1_RANGE) item_is_type[i]["MED 1"] == 1;
  forall(i in MED2_RANGE) item_is_type[i]["MED 2"] == 1;
  forall(i in MED3_RANGE) item_is_type[i]["MED 3"] == 1;
  forall(i in DRONE_RANGE) (sum(j in Drones) item_is_type[i][j]) == 1;
  
}