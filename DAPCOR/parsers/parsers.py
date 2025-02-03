'''
This code was originally shared under the MIT License by Business Science (https://github.com/business-science).
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

# import packages
from langchain_core.output_parsers import BaseOutputParser
import re

# Python Parser for output standardization  
class PythonOutputParser(BaseOutputParser):
    def parse(self, text: str):        
        def extract_python_code(text):
            python_code_match = re.search(r'```python(.*?)```', text, re.DOTALL)
            if python_code_match:
                python_code = python_code_match.group(1).strip()
                return python_code
            else:
                python_code_match = re.search(r"python(.*?)'", text, re.DOTALL)
                if python_code_match:
                    python_code = python_code_match.group(1).strip()
                    return python_code
                else:
                    return None
        python_code = extract_python_code(text)
        if python_code is not None:
            return python_code
        else:
            # Assume ```python wasn't used
            return text

# SQL Parser for output standardization  
class SQLOutputParser(BaseOutputParser):
    def parse(self, text: str):        
        def extract_sql_code(text):
            sql_code_match = re.search(r'```sql(.*?)```', text, re.DOTALL)
            sql_code_match_2 = re.search(r"SQLQuery:\s*(.*)", text)
            if sql_code_match:
                sql_code = sql_code_match.group(1).strip()
                return sql_code
            if sql_code_match_2:
                sql_code = sql_code_match_2.group(1).strip()
                return sql_code
            else:
                sql_code_match = re.search(r"sql(.*?)'", text, re.DOTALL)
                if sql_code_match:
                    sql_code = sql_code_match.group(1).strip()
                    return sql_code
                else:
                    return None
        sql_code = extract_sql_code(text)
        if sql_code is not None:
            return sql_code
        else:
            # Assume ```sql wasn't used
            return text
