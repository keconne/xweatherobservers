Readme-Datasets.txt 2023-02-20

Assets are stored in the apps 'User' subfolder. Shared assets loaded
at startup are kept in 'User/_Global_/...', ie:

- 'User/_Global_/images/Earth.jpg' (general use texture)

- 'User/_Global_/models/jeep.3ds'
- 'User/_Global_/models/jeep.jpg' (texture belonging to a 3D model)

It also contains the startup settings and 'Preset' paths (keys: 1, 2 or 3).

- 'User/_Global_/csv/np_globals.csv'
- 'User/_Global_/cs/np_preset.cvs'

(*Currently) all datasets are kept 4 levels deep (from the app) to allow
for their [Dataset-Name]_npe.bat to be able to launch a dataset from the
OS File Manager. We suggest this (but do not require it):

User/[Category]/[Sub-Cat]/[Dataset-Name]/..._npe.bat

eg: 'User/GaiaViz/RSSviz/ChatGPT/ChatGPT_npe.bat

We are agnostic to the datasets base folder name and (CSV) file names.
But do encourage separating assets by type:

- 'User/GaiaViz/RSSviz/Ukraine/csv/Ukraine_np_node.csv'
- 'User/GaiaViz/RSSviz/Ukraine/images/Earth-BW.jpg'

However, we have a version convention that appends the '_v[##]' to the
folder, but not the files:

- 'User/GaiaViz/RSSviz/Ukraine_v02/csv/Ukraine_np_node.csv'


--- Future Notes ---

* Future feature, create a launcher utility/app called 'NPE.exe' that
redirects the dataset to a chosen app version (ANTz, ANTz+Xr, GaiaViz).
Adding it to the path also solves the directory depth problem .bat files.

**Future feature, embedding dataset folders. If you place a dataset
folder into another datasets sub-directories, then it would load with
the dataset, either onto the root grid or onto a sub-grid.


***Other global forders are for future use ('av', 'json', 'plugins'...)
