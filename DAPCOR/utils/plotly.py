'''
The code in this script is adapted from AI Data Science Team (https://github.com/business-science/ai-data-science-team).
The original code was shared under the MIT License which reads as follows:

Copyright (c) 2024 ai-data-science-team authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Adapted by: Ankur Kumar @ ProcessIndustryAI LLC [January 2025]

'''

import json
import plotly.io as pio

def plotly_from_dict(plotly_graph_dict: dict):
    """
    Convert a Plotly graph dictionary to a Plotly graph object.
    
    Parameters:
    -----------
    plotly_graph_dict: dict
        A Plotly graph dictionary.
        
    Returns:
    --------
    plotly_graph: plotly.graph_objs.graph_objs.Figure
        A Plotly graph object.
    """
    
    if plotly_from_dict is None:
        return None
    
    return pio.from_json(json.dumps(plotly_graph_dict))