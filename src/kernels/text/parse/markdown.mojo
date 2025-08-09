from python import Python

fn parse_inline_markdown(text: String) -> String:
    """Parse inline markdown elements like bold and italic"""
    var result = text
    
    # Simple bold replacement - **text** -> <strong>text</strong>
    # This is a basic implementation
    var idx = 0
    var output = String("")
    var in_bold = False
    
    while idx < len(result):
        if idx < len(result) - 1 and result[idx] == '*' and result[idx + 1] == '*':
            if not in_bold:
                output += "<strong>"
                in_bold = True
            else:
                output += "</strong>"
                in_bold = False
            idx += 2
        else:
            output += result[idx]
            idx += 1
    
    return output

fn text_parse_markdown_kernel(markdown_text: String) -> String:
    """
    Convert markdown to HTML
    
    Args:
        markdown_text: Markdown formatted text
        
    Returns:
        HTML string
    """
    var lines = markdown_text.split("\n")
    var html_output = String("")
    var in_paragraph = False
    
    for i in range(len(lines)):
        let line = lines[i]
        
        if len(line) == 0:
            if in_paragraph:
                html_output += "</p>\n"
                in_paragraph = False
            continue
        
        # Handle headers
        if line.startswith("# "):
            if in_paragraph:
                html_output += "</p>\n"
                in_paragraph = False
            html_output += "<h1>" + parse_inline_markdown(line[2:]) + "</h1>\n"
        elif line.startswith("## "):
            if in_paragraph:
                html_output += "</p>\n"
                in_paragraph = False
            html_output += "<h2>" + parse_inline_markdown(line[3:]) + "</h2>\n"
        elif line.startswith("### "):
            if in_paragraph:
                html_output += "</p>\n"
                in_paragraph = False
            html_output += "<h3>" + parse_inline_markdown(line[4:]) + "</h3>\n"
        else:
            # Regular paragraph
            if not in_paragraph:
                html_output += "<p>"
                in_paragraph = True
            else:
                html_output += " "
            html_output += parse_inline_markdown(line)
    
    if in_paragraph:
        html_output += "</p>\n"
    
    return html_output

fn main():
    let md = "# Hello World\n\nThis is **bold** text.\n\nAnother paragraph here."
    let html = text_parse_markdown_kernel(md)
    print("Input markdown:")
    print(md)
    print("\nOutput HTML:")
    print(html)