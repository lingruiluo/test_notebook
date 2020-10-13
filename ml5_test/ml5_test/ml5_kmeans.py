from . import ml5_init
from . import utilis
import jp_proxy_widget
from IPython.display import display
from jupyter_ui_poll import ui_events
import time


class Kmeans(ml5_init.ML5Class):

    def __init__(self, options=None, data = None, *pargs, **kwargs):
        super(Kmeans,self).__init__(options=options,*pargs, **kwargs)
        self.data = []
        if data is not None:
            self.data = data
        self.data_label = []
        self.js_init("""
            element.nn_info = {};
            element.nn_info.data = input_data;
        """,input_data = self.data)
        self.element.html("Loaded ml5.js")
    
    def default_options(self):
        return {
            'k': 3,
            'maxIter': 4,
            'threshold': 0.5,
        }

    def initialize(self, data=None, options=None):
        
        def data_label_callback(info):
            self.data_label.append(info)
        
        self.train_done = False
        def done_callback():
            self.train_done = True
        
        if data is None:
            data = self.data
        else:
            self.data = data
        if options is None:
            options = self.options
        
        self.js_init("""
            function clustersCalculated() {
                console.log('Points Clustered!');
                element.nn_info.output = kmeans.dataset;
                console.log(kmeans.dataset);
                for (x = 0; x < kmeans.dataset.length; x++){
                    data_label_callback(kmeans.dataset[x].centroid);
                }
                console.log("all done:)");
            }
            //const data = element.nn_info.data;
            const kmeans = ml5.kmeans(data, options, clustersCalculated);
            element.nn_info.network=kmeans;
            done_callback();
        """, data = data, options = options, data_label_callback = data_label_callback,
             done_callback =done_callback)
        with ui_events() as poll:
            while self.train_done is False:
                poll(10)  
                time.sleep(0.1)
        print('done')
    
    def add_data(self, single_data, data_type = None):
        '''
        csv: should be a path for data file
        '''
        self.js_init("""
            element.nn_info.data.push(single_data);
        """,single_data = single_data)
        