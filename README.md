# 🛣️ Spatial Line Cluster

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-3CB371?style=for-the-badge&logo=python&logoColor=white)

A Python tool for clustering geometries based on spatial proximity. Built with GeoPandas for geospatial operations and graph-based clustering algorithms, this respository provides an efficient solution for grouping linear features in GIS workflows. 

# 🧭 Overview
This repository provides tools to cluster LineStrings based on spatila proximity. Leveraging the power of GeoPandas and NetworkX, the tool uses graph-based algorithms to identify and group nearby geometries

**🛠️Key Features**

* Seamless Integration: Accepts standard Pandas DataFrames as input and handles convertion to GeoDataFrames.
* Graph-Based Clustering: Utilizes NetworkX to build spatial graphs where nodes represent geometries and edges represent proximity.
* Customizable Precision: Features a configurable tolerance parameter (in meters) to define the proximity threshold for clustering.

**Versions**

|Version|Description|
|-|-|
|v0.1.0|Initial Version|

**Class Methods**
|Method|Description|Returns|
|-|-|-|
|build_geodataframe|Function to convert a DataFrame to GeoDataFrame.|gpd.GeoDataFrame object|
|determine_utm_and_reproject|Determine the appropriate UTM zone for a geometry and calculate its length in meters.|tuple of (int, float) EPSG of the area and the length of the line|
|add_utm_projection_metrics|Add UTM projection information and metric lengths to a GeoDataFrame.|gpd.GeoDataFrame. A copy of the input GeoDataFrame with two additional columns: 1) 'utm_epsg' (int): The EPSG code of the determined UTM zone for each geometry; 2) 'len_mt' (float): The length of each geometry|
|group_geometries_by_proximity|This function identifies clusters of geometries (lines, polygons, etc.) that are touching or within a specified distance tolerance|int: The input GeoDataFrame with an additional 'parking_id' column|
|process_clustering|Execute the complete spatial clustering pipeline for geometries.|Clustered gdf.GeoDataFrame|


# ⚙️ Installation

**Prerequisites**

* Python > 3.10

1. Clone the repository:
   ```bash
   git clone https://github.com/r3card0/Spatial-Line-Cluster.git
   ```
2. Install as a dependency
   Alternatively, you can install it as a dependency withib your own project:
    * Create a Python Virtual Environment
        ```
        python3 -m venv venv_test
        ```
    * Activate virtual environment
        ```
        source vene_test/bin/activate
        ```
    * 📦 Install repository as a dependency:
        ```
        pip install git+https://github.com/r3card0/Spatial-Line-Cluster.git@0.1.0
        ```
        The following libraries will be installed:
        ```
        certifi==2026.1.4
        geopandas==1.1.2
        networkx==3.4.2
        numpy==2.2.6
        packaging==26.0
        pandas==2.3.3
        pyogrio==0.12.1
        pyproj==3.7.1
        python-dateutil==2.9.0.post0
        pytz==2025.2
        shapely==2.1.2
        six==1.17.0
        tzdata==2025.3
        ```

# 🚗 Usage
**Example to use as a dependency**

```python
# Import process
from spatial_line_cluster import SpatialLineCluster
import pandas as pd

# Create a DataFrame 
file_base = "data_lines.csv"

def run_testing():
    print("Start to create a DataFrame")
    df = pd.read_csv(file_base)
    print("DataFrame successfully created")

    # Taking a sample of the original DataFrame
    print("Creating a sample . . .")
    df_test = df[(df['state'] == 'New York') & (df['city'] == 'New York')].reset_index() # Reset original index
    print("Sample of the DataFrame")

    print("Applying Spatial Line cluster class")
    # Initiate
    try1 = SpatialLineCluster()

    # Convert from DataFrame to GeoDataFrame
    gdf = try1.build_geodataframe(df_test,"geom","EPSG:4326")

    print(f"Creating the clusterds of New York city...")
    df_cluster = try1.process_clustering(gdf,"geometry",0.001)
    print("Clustering process completed ✅")
    df_cluster = df_cluster.sort_values(["parking_id","state","city"])

    return df_cluster



def run():
    print(run_testing())

if __name__ == "__main__":
    run()
```


**Example of use in a cloned repository**

```python
import sys
from pathlib import Path

# Add the root of the project
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.spatial_line_cluster import SpatialLineCluster

import pandas as pd

# Create a DataFrame 
file_base = "data_lines.csv"

def run_testing():
    print("Start to create a DataFrame")
    df = pd.read_csv(file_base)
    print("DataFrame successfully created")

    # Taking a sample of the original DataFrame
    print("Creating a sample . . .")
    df_test = df[(df['state'] == 'New York') & (df['city'] == 'New York')].reset_index() # Reset original index
    print("Sample of the DataFrame")

    print("Applying Spatial Line cluster class")
    # Initiate
    try1 = SpatialLineCluster()

    # Convert from DataFrame to GeoDataFrame
    gdf = try1.build_geodataframe(df_test,"geom","EPSG:4326")

    print(f"Creating the clusterds of New York city...")
    df_cluster = try1.process_clustering(gdf,"geometry",0.001)
    print("Clustering process completed ✅")
    df_cluster = df_cluster.sort_values(["parking_id","state","city"])

    return df_cluster



def run():
    print(run_testing())

if __name__ == "__main__":
    run()
```

# 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

# 🔗 References
**GeoPandas**
* [Method - estimate_utm_crs](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.estimate_utm_crs.html)
* [Method - sindex](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.sindex.html)
* [Method - buffer](https://geopandas.org/en/stable/getting_started/introduction.html#Buffer)
* [Method - intersects](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.intersects.html)

**Networkx**
* [Networkx - Documentation](https://networkx.org/documentation/stable/tutorial.html)
* [Method - add_nodes_from](https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.add_nodes_from.html)
* [Method - add_edge](https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.add_edge.html)

**Pandas**
* [DataFrame.apply](https://pandas.pydata.org/pandas-docs/dev/reference/api/pandas.DataFrame.apply.html)


# 👤 Author

* GitHub: [r3card0](https://github.com/r3card0)
* LinkedIn: [Ricardo](https://www.linkedin.com/in/ricardordzsaldivar/)