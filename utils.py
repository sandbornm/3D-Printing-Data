import pandas as pd
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import zipfile

NAMES = ["arm_failure", "bowden", "plastic", "proper", "retraction", "unstick"]

class PrintData:
    def __init__(self, name):
        assert name in NAMES
        self.name = name
        """ dataframe """
        self.unzip()
        self.df = self.readData()
        self.fig = self.vizData()

    def unzip(self):
        p = os.path.join(os.getcwd(), "four_towers", self.name)
        print(p)
        with zipfile.ZipFile(os.path.join(p,self.name+".zip"), 'r') as zf:
            zf.extractall(os.path.join(p))

    def readData(self):
        fp = os.path.join(os.getcwd(), "four_towers", self.name, self.name)
        files = [x for x in os.listdir(fp) if x[-3:] == "txt"]
        print(f"path {fp}")
        print(files)
        fname = os.path.join(fp, files[0])
        df = pd.read_csv(fname, low_memory=False, names=['data_id', 'accel0X',
                                     'accel0Y', 'accel0Z',
                                     'accel1X', 'accel1Y',
                                     'accel1Z', 'tension',
                                     'timestamp'])

        # normalize time
        df["timestampNorm"] = df["timestamp"] - df["timestamp"][0]
        print(f"part name: {self.name}")
        print(f"{len(df)} before dropping duplicates")
        # remove duplicates
        df.drop_duplicates(inplace=True, subset="timestampNorm")
        print(f"{len(df)} after dropping duplicates")
        print(df["timestampNorm"])

        return df

    def __repr__(self):
        return self.name
    
    """ visualize accelerations and tensions over time on 2 plots"""
    def vizData(self):
        fig = make_subplots(shared_xaxes=True, rows=3, cols=1, vertical_spacing=0.05, subplot_titles=("Acceleration 1 XYZ", "Acceleration 2 XYZ", "Tension"))
        time = self.df["timestampNorm"]

        # accel 0
        accel0 = (self.df["accel0X"], self.df["accel0Y"], self.df["accel0Z"]) 
        dirs = ("x", "y", "z") 

        for (acc, dir) in list(zip(accel0, dirs)):
            fig.add_trace(
                go.Scatter(x=time, y=acc, name=f"acc_{dir}"), row=1, col=1
            )

        # accel 1
        accel1 = (self.df["accel1X"], self.df["accel1Y"], self.df["accel1Z"])

        for (acc, dir) in list(zip(accel1, dirs)):
            fig.add_trace(
                go.Scatter(x=time, y=acc, name=f"acc_{dir}"), row=2, col=1
            )

        # tension
        tension = self.df["tension"]
        fig.add_trace(
                go.Scatter(x=time, y=tension, name="tension"), row=3, col=1
        )

        fig['layout']['xaxis3']['title']='time (ms)'
        fig['layout']['yaxis']['title']='acceleration (mm/s^2)'
        fig['layout']['yaxis3']['title']='tension (mN ?)'

        fig.update_layout(title_text=f"{self.name} printing data")
        return fig


""" Remove the """
def cleanUp():
    base = os.path.join(os.getcwd(), "four_towers")
    fls = os.listdir(base)
    for f in fls:
        d = os.path.join(base, f)
        if os.path.isdir(d):
            print(os.listdir(d))

# data = {}
# for name in NAMES[-1:]:
#     data[name] = PrintData(name)


# remove unzipped files to prevent github yelling
cleanUp()

# test
# pr = PrintData("proper")
# pr.fig.show()