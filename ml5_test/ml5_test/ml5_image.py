from . import ml5_init
from . import utilis
import jp_proxy_widget
from IPython.display import display
from jupyter_ui_poll import ui_events
import numpy as np
import time


class imageClassifier(ml5_init.ML5Class):

    def __init__(self, model, options=None, *pargs, **kwargs):
        super(imageClassifier,self).__init__(options=options,*pargs, **kwargs)
        self.data = []
        if options is None:
            options = self.default_options()
        self.element.html("Loaded ml5.js")
        self.classify_callback_list = []
        self.classify_done = False
        self.model_load = False
        def model_ready():
            self.model_load = True

        self.js_init("""
            element.nn_info = {};
            const image_model = ml5.imageClassifier(model, modelReady);
            element.nn_info.network = image_model;
            function modelReady() {
                console.log('Model Ready!');
                model_ready()
            }
        """,model = model,model_ready=model_ready)
        with ui_events() as poll:
            while self.model_load is False:
                poll(10)
                print('.', end='')
                time.sleep(0.1)
        print('Modeal is ready')
    
    def default_options(self):
        return {'version': 1,'alpha': 1.0,'topk': 3,}

    def classify_data(self, image, width=400, height=400, 
                    num_of_class = 3, callback=None):
        if callback is None:
            callback = self.classify_callback
        
        self.classify_done = False
        def done_callback():
            self.classify_done = True
        if isinstance(image,str):
            self.js_init("""
                function handleResults(error, result) {
                    if(error){
                    console.error(error);
                    return;
                    }
                    console.log(result);
                    callback(result);
                    done_callback();
                }
                var img = document.createElement("img");
                img.src = src;
                img.width = width;
                img.height = height;
                element.nn_info.network.classify(img, num_of_class, handleResults);

            """, src=image, width=width, height=height,
                num_of_class = num_of_class,
                callback=callback, done_callback = done_callback)
            with ui_events() as poll:
                while self.classify_done is False:
                    poll(10)                # React to UI events (upto 10 at a time)
                    print('.', end='')
                    time.sleep(0.1)
            print('done')
        else:
            if isinstance(image,np.ndarray):
                if len(image.shape)==1:
                    if width*height!=image.shape[0]:
                        raise ValueError('image shape should be consistent with width and height')
                elif len(image.shape)==2:
                    raise ValueError("Please provide a rgba image pixel array")
                else:
                    if image.shape[2]!=4:
                        raise ValueError("Please provide a rgba image pixel array")
                    else:
                        image = image.flatten()
                image = image.tolist()
            self.js_init("""
                var canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                var ctx = canvas.getContext('2d');
                var imgData=ctx.getImageData(0,0,width,height);
                imgData.data.set(d);
                function handleResults(error, result) {
                    if(error){
                    console.error(error);
                    return;
                    }
                    console.log(result);
                    callback(result);
                    done_callback();
                }
                element.nn_info.network.classify(imgData, num_of_class, handleResults);
            """,d = image, width=width, height=height,
                num_of_class = num_of_class,
                callback=callback, done_callback = done_callback)
            with ui_events() as poll:
                while self.classify_done is False:
                    poll(10)                # React to UI events (upto 10 at a time)
                    print('.', end='')
                    time.sleep(0.1)
            print('done')