from pathlib import Path
from typing import List, Tuple


# Structured Functional Test Language file
# Script Recording Language file


def parse_srl_custom(line: str) -> Tuple[str, str, str]:
    """
    Custom parser for .srl lines with format 'source type~target'.
    
    Args:
        line (str): The line to parse, e.g. 'path\\to\\file binary~file.bin'
    
    Returns:
        Tuple[str, str, str]: (source, type, target)
    """
    if '~' not in line:
        raise ValueError("Missing '~' delimiter in line")

    source_and_type, target = line.strip().split("~")
    target = target.strip()

    known_types = {"binary", "text"}

    # Backtrack from end to find last space separating type
    source, sep, file_type = source_and_type.rpartition(" ")

    # If we can't find a valid type, treat whole thing as source
    if file_type not in known_types:
        file_type = ""
        source = source_and_type.strip()

    return Path(rf"{source.strip()}"), file_type.strip(), target.strip()


def generate_filexfer_block(source: str, file_type: str, target: str) -> str:
    """
    Generates an XML filexfer block for the given file transfer details.
    
    Args:
        source (str): The source file path on the PC.
        file_type (str): The type of file transfer, e.g., 'binary'.
        target (str): The destination file name on the host.
    
    Returns:
        str: A string containing the XML <filexfer> block with pause.
    """
    options = 'RECFM(V)' if file_type.lower() == 'binary' else ''
    return (
        f'\t\t\t<filexfer direction\="send" hostfile\="{target}" '
        f'pcfile\="{source}" options\="{options}" clear\="false" '
        'timeout\="30" pccodepage\="437" mtusize\="2500"  />\r\n'
        '\t\t\t<pause value\="1500" />\r\n'
    )


def convert_srl_to_sftl(srl_lines: List[str]) -> str:
    """
    Converts a list of .srl lines to an .sftl XML format.
    
    Args:
        srl_lines (List[str]): Lines read from a .srl file.
    
    Returns:
        str: A string containing the formatted .sftl XML content.
    """
    header = (
        '#Auto-generated SFTL file\r\n'
        'code=<HAScript name\="" description\="" timeout\="60000" pausetime\="300" '
        'promptall\="true" blockinput\="false" author\="" creationdate\="" '
        'supressclearevents\="false" usevars\="false" ignorepauseforenhancedtn\="true" '
        'delayifnotenhancedtn\="0" ignorepausetimeforenhancedtn\="true">\r\n\r\n'
        '\t<screen name\="Screen1" entryscreen\="true" exitscreen\="true" transient\="false">\r\n'
        '\t\t<description >\r\n'
        '\t\t\t<oia status\="NOTINHIBITED" optional\="false" invertmatch\="false" />\r\n'
        '\t\t</description>\r\n'
        '\t\t<actions>\r\n'
    )

    footer = (
        '\t\t</actions>\r\n'
        '\t\t<nextscreens timeout\="0" >\r\n'
        '\t\t</nextscreens>\r\n'
        '\t</screen>\r\n\r\n'
        '</HAScript>\r\n'
        'hostType=MVS/TSO\r\n'
        'version=400\r\n'
        'direction=SEND\r\n'
    )

    body = ''
    for line in srl_lines:
        if line.strip():
            source, file_type, target = parse_srl_custom(line)
            body += generate_filexfer_block(source, file_type, target)

    return header + body + footer


def write_sftl_to_file(sftl_content: str, output_path: str = "output.sftl") -> None:
    """
    Writes the .sftl content to a file with Windows CRLF line endings.
    
    Args:
        sftl_content (str): The complete XML content to be written.
        output_path (str): The filename to save the .sftl output as. Defaults to 'output.sftl'.
    """
    if not output_path.endswith('.sftl'):
        output_path += '.sftl'
    with open(output_path, "w", encoding="utf-8", newline="\r\n") as f:
        lines = sftl_content.splitlines()
        f.write('\r\n'.join(lines) + '\r\n')


def main(srl_file_path: str, sftl_output_path: str = "output.sftl") -> None:
    """
    Main function to convert .srl to .sftl and save the result.
    
    Args:
        srl_file_path (str): Path to the .srl input file.
        sftl_output_path (str): Path to save the output .sftl file.
    """
    srl_path = Path(srl_file_path)
    if not srl_path.exists():
        raise FileNotFoundError(f"Input .srl file not found: {srl_file_path}")

    with open(srl_path, "r", encoding="utf-8") as file:
        srl_lines: List[str] = file.readlines()


    print(srl_lines, end = "\n")
    print(len(srl_lines), end = "\n")
    sftl_content = convert_srl_to_sftl(srl_lines)
    print(sftl_content)
    write_sftl_to_file(sftl_content, sftl_output_path)


# Example usage
if __name__ == "__main__":
    main("pcommSEND.srl", "output.sftl") 


