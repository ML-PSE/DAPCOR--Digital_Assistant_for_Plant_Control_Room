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

import os

def log_ai_function(response: str, file_name: str, log: bool = True, log_path: str = './logs/', overwrite: bool = True):
    """
    Logs the response of an AI function to a file.
    
    Parameters
    ----------
    response : str
        The response of the AI function.
    file_name : str
        The name of the file to save the response to.
    log : bool, optional
        Whether to log the response or not. The default is True.
    log_path : str, optional
        The path to save the log file. The default is './logs/'.
    overwrite : bool, optional
        Whether to overwrite the file if it already exists. The default is True.
        - If True, the file will be overwritten. 
        - If False, a unique file name will be created.
    
    Returns
    -------
    tuple
        The path and name of the log file.    
    """
    
    if log:
        # Ensure the directory exists
        os.makedirs(log_path, exist_ok=True)
        file_path = os.path.join(log_path, file_name)

        if not overwrite:
            # If file already exists and we're NOT overwriting, we create a new name
            if os.path.exists(file_path):
                base_name, ext = os.path.splitext(file_name)
                i = 1
                while True:
                    new_file_name = f"{base_name}_{i}{ext}"
                    new_file_path = os.path.join(log_path, new_file_name)
                    if not os.path.exists(new_file_path):
                        file_path = new_file_path
                        file_name = new_file_name
                        break
                    i += 1

        # Write the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response)

        print(f"      File saved to: {file_path}")
        
        return (file_path, file_name)
    
    else:
        return (None, None)