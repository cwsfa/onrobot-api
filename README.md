# onrobot-api

This is a repository for Python API of OnRobot grippers. The `script` folder includes modules for **RG2**, **2GF7** and **VGC10** gripper models.

---

## Gripper Status

|  Status | Description  |
|---|---|
| 0 | Stable |
| -1 | Error |
| -2 | Connection Failed  |

---

## Python API reference for **2FG7**


|  Methods | Description  |  Input |
|---|---|---|
| grip  | Moves the gripper to the desired position  | **t_width**: *Default=20.0 (mm)*, **n_force**: *Default=20 (N)*, **p_speed**: *Default=10(%)*, **f_wait**: *Default=True*  |
| move  | Moves the gripper to the desired position  | **t_width**: *Default=20.0 (mm)*, **f_wait**: *Default=True*|
| isConnected  | Returns **True** if the gripper is connected, **False** otherwise  | - |
| isBusy  | Returns **True** if there is an obstacle during operation, **False** otherwise   | - |
| isGripped  | Returns **True** if an object is gripped, **False** otherwise   | - |
| getStatus  | Returns current status of the gripper (No connection=-2, Error=-1, Stable=0)  | - |
| get_ext_width  | Returns current width between fingers | - |
| get_force  | Returns current force on the gripper (in Newton) | - |
| stop  | Stops the action  | - |
| get_min_ext_width  | Returns minimum gripping width  | - |
| get_max_ext_width  | Returns minimum gripping width  | - |

### **Input parameter explanation**

- **t_width**: width to move the gripper to in mm's (*float*)
- **n_force**: force to move the gripper width in N (*float*)
- **p_speed**: speed of the gripper in % compared to full speed (*int*)
- **f_wait**: wait for the gripper to end or not (*Boolean*)

### **Example script for 2FG7**

```python
from device import Device
from twofg import TWOFG

device = Device()
gripper = TWOFG(device)
gripper.isConnected()   # for checking connection
```

---

## Decoding byte string to a python script

run `api_byte2script.py` to create `api_original.py` in the current directory

```bash
python3 /path/to/onrobot-api/api_byte2script.py
```
