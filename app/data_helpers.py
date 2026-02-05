import pandas as pd

def get_schools_for_university(file_path, university):
    """
    Get available schools for a specific university.
    
    Args:
        file_path: Path to the cleaned CSV file
        university: University name
    
    Returns:
        list: Sorted list of school names
    """
    if not university:
        return []
    
    df = pd.read_csv(file_path)
    schools = sorted(df[df['university'] == university]['school'].unique().tolist())
    return schools

def get_degrees_for_university_school(file_path, university, school=None):
    """
    Get available degrees for a specific university and optional school.
    
    Args:
        file_path: Path to the cleaned CSV file
        university: University name
        school: School name (optional)
    
    Returns:
        list: Sorted list of degree names
    """
    if not university:
        return []
    
    df = pd.read_csv(file_path)
    filtered = df[df['university'] == university]
    
    if school:
        filtered = filtered[filtered['school'] == school]
    
    degrees = sorted(filtered['degree'].unique().tolist())
    return degrees
