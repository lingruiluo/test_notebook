"""
Framework for wrapping 
"""

import jp_proxy_widget
from IPython.display import display


def load_requirements(widget=None, silent=True, additional=()):
    """
    Load Javascript prerequisites into the notebook page context.
    """
    if widget is None:
        widget = jp_proxy_widget.JSProxyWidget()
        silent = False
    # Make sure jQuery and jQueryUI are loaded.
    widget.check_jquery()
    # load additional jQuery plugin code.
    ml5_js = ["https://unpkg.com/ml5@0.5.0/dist/ml5.min.js"]
    widget.load_js_files(ml5_js)
    if not silent:
        widget.element.html("<div>Requirements for <b>chart_ipynb</b> have been loaded.</div>")
        display(widget)

class ML5Class(jp_proxy_widget.JSProxyWidget):
    

    def __init__(self, options=None, *pargs, **kwargs):
        super(ML5Class, self).__init__(*pargs, **kwargs)
        load_requirements(self)
        self.element.html("Loaded ml5.js")
        if options is None:
            options = self.default_options()
        self.options = options

    def default_options(self):
        return {
            'inputs': [],
            'outputs': [],
            'dataUrl': None,
            'modelUrl': None,
            'layers': [],
            'task': None,
            'debug': False,
            'learningRate': 0.2,
            'hiddenUnits': 16,
        }

    def add_layer(self, layer):
        if 'layers' in self.options:
            self.options['layers'].append(layer)
        else:
            self.options['layers'] = [layer]

    def initialize_framework(self, options):
        
        self.js_init("""
            element.empty();

            const nn = ml5.neuralNetwork(options);
            element.nn_info = {
                network: nn };
        """, options = options)

    def add_data(self, inputs, outputs):
        self.js_init("""
            element.nn_info.network.addData(inputs, outputs);
        """, inputs = inputs, outputs = outputs)

    
    def normalize_data(self):
        self.js_init("""
            element.nn_info.network.normalizeData();
        """)

    def train_data(self, trainingOptions):
        self.js_init("""
            function doneTraining() {
                console.log('done!');
            }
            function whileTraining(epoch, loss) {
                console.log(`epoch: ${epoch}, loss:${loss}`);
            }
            function doneTraining() {
                console.log('done!');
            }
            element.nn_info.network.train(whileTraining, doneTraining);

        """)#,trainingOptions = trainingOptions)

    def classify_data(self, input, callback=None):
        if callback is None:
            callback = self.classify_callback
        self.js_init("""
            function handleResults(error, result) {
                if(error){
                console.error(error);
                return;
                }
                console.log(result);
                callback(result);
            }
            element.nn_info.network.classify(input, handleResults);

        """, input=input, callback=callback)
    
    classify_callback_list = []
    def classify_callback(self, info):
        classify_callback_list.append(info)


    def predict_data(self, input, callback=None):
        if callback is None:
            callback = self.predict_callback
        self.js_init("""
            function handleResults(error, result) {
                if(error){
                console.error(error);
                return;
                }
                console.log(result);
                callback(result);
            }
            element.nn_info.network.predict(input, handleResults);

        """, input=input, callback=callback)
    predict_callback_list = []
    def predict_callback(self, info):
        predict_callback_list.append(info)