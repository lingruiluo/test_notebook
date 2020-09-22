import numpy as np

def clean_dict(**kwargs):
    "Like dict but with no None values make some values JSON serializable"
    # XXXX this should move to jp_proxy_widgets
    result = {}
    for kw in kwargs:
        v = kwargs[kw]
        if v is not None:
            if isinstance(v, np.ndarray):
                # listiffy arrays -- maybe should be done elsewhere
                v = v.tolist()
            if isinstance(v, np.floating):
                v = float(v)
            if type(v) is tuple:
                v = list(v)
            result[kw] = v
    return result

def options(
        task,
        inputs = [],
        outputs = [],
        layers=[],
        debug = False,
        learningRate = 0.2,
        hiddenUnits = 16,
        dataUrl=None,
        modelUrl=None,
        **other_arguments
    ):
    return clean_dict(
        task = task,
        inputs = [],
        outputs = [],
        layers = layers,
        debug = debug,
        learningRate = learningRate,
        hiddenUnits = hiddenUnits,
        dataUrl = dataUrl,
        modelUrl = modelUrl,
        **other_arguments
    )

def layer(
        type,
        activation,
        **other_arguments,
    ):
    return clean_dict(
        type = type,
        activation=activation,
        **other_arguments
    )
