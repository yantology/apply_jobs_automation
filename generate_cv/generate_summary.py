"""
Generate a summary for a CV from a YAML file.
"""

from .models import CV
from openai import OpenAI

def generate_summary(cv:CV,vacancy: str) -> str:
    """
    Generate a summary for a CV.
    
    Args:
        cv: CV object containing the CV data
        vacancy: The job vacancy for which the CV is being tailored
        
    Returns:
        A string summary of the CV
    """
    openai = OpenAI(
        base_url="http://localhost:4000",  # Your proxy URL
        api_key="sk-1234"             # Your proxy API key
    )
    prompt = f"""
    Generate a summary for the following CV tailored to the job vacancy: 
    {vacancy}
    
    CV:
    {cv.model_dump_json(indent=2)}
    
    Summary:
    """
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
            Summarize the CV in no more than 3 sentences. 
            related with vacancy.dont be too formal. 
            Dont add name and contact. 
            Dont too detail.
            Dont make over I just Junior.
            just a summary.
            """},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content

    print(content)
    return content if content is not None else ""
