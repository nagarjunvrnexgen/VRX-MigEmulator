import streamlit as st 
import pandas as pd 
from parse import convert_srl_to_sftl, write_sftl_to_file


hcl_df: pd.DataFrame = pd.DataFrame(
    {
        'hcl_key': [
            'B27','M86','T16777232','C127','S33554442','T16777234','T16777233',
            'S40','B155','C120','B33','B34','B35','S127','M90','B36','B37','B38',
            'B39','keyVersion','B8','B9','B40','C33554559','C65','C67','S9','T16777373',
            'A123','B33554587','B33554466','B33554467','B33554465','B33554468',
            'sessionType','codePage','C74','C77','S33554559','B226','B227',
            'B224','B225','C155','S155','T16','C80','T18','T17','C82','C81','C83',
            'C86','C85','C88','B118','B119','B116','B117','B114','C16777233',
            'B115','B112','B113','C33554467','B33554442','C33554468','C33554465',
            'C33554466','C33554587','T157','C90','XF:[textlogicaldisp]',
            'autoApply','C17','B127','B123','B121','B122','XF:[textvisualdisp]',
            'S10','B120','S119','S117','S118','S115','S116','S113','S114','S33554468',
            'C227','C226','C225','S33554587','C224','M67','S122','S123','S27',
            'S120','disableKeyBuffer','S121','B10','S227','C33','C35','S225','S226',
            'C34','C37','C36','S224','C39','C38','C119','B19','B33554559','S37','S36',
            'S39','S112','S38','C40'
        ],
        'hcl_value': [
            '[clear]','55','16777232','[deleteword]','[newline]','16777234','16777233',''
            '[markdown]','[insert]','[cursel]','[pageup]','[pagedn]','[eof]','53','|206',
            '[home]','[left]','[up]','[right]','2','[backspace]','[tab]','[down]',
            '[deleteword]','57','54','[backtab]','16777373','[+cr]','[insert]','[pagedn]',
            '[eof]','[pageup]','[home]','1','037','49','|26','53','[left]',
            '[right]','[up]','[down]','54','55','16','|35','18','17','|62',
            '51','|11','55','|24','53','[pf7]','[pf8]','[pf5]','[pf6]','[pf3]',
            '[enterreset]','[pf4]','[pf1]','[pf2]','[backtabword]','[enter]',
            '[rule]','49','[tabword]','54','157','|206','[textlogicaldisp]','false',
            '[enterreset]','[delete]','[pf12]','[pf10]','[pf11]','[textvisualdisp]',
            '[newline]','[pf9]','[pf20]','[pf18]','[pf19]','[pf16]','[pf17]','[pf14]',
            '[pf15]','[fieldmark]','[moveright]','[moveleft]','[movedown]','55',
            '[moveup]','54','[pf23]','[pf24]','[unmark]','[pf21]','false','[pf22]',
            '[enter]','[markright]','49','[backtabword]','[markdown]','[markleft]',
            '|235','[moveleft]','[rule]','[markup]','[moveright]','[moveup]',
            '[aplkbd]','[clear]','[delete]','[markleft]','[fieldmark]','[markright]',
            '[pf13]','[markup]','[movedown]'
            ]
    }
)

pcom_to_zie_keymap: dict[str, str] = {
    "KEY112": "B112",
    "KEY113": "B113",
    "KEY114": "B114",
    "KEY115": "B115",
    "KEY116": "B116",
    "KEY117": "B117",
    "KEY118": "B118",
    "KEY119": "B119",
    "KEY120": "B120",
    "KEY121": "B121",
    "KEY122": "B122",
    "KEY123": "B123",
}

def get_pcom_df(pcom_content: list[str]) -> pd.DataFrame:
    
    pcom_df =  pd.Series(pcom_content[4:])\
        .str.replace("\n", "")\
        .str.split("=", expand = True)\
        .rename(
            columns = {
                0: "pcom_key",
                1: "pcom_value"
            }
        )
    
    pcom_df["pcom_zie_mapper"] = pcom_df["pcom_key"].replace(pcom_to_zie_keymap)

    return pcom_df



def get_final_df(pcom_df: pd.DataFrame) -> pd.DataFrame:
    final_df = pd.merge(
        hcl_df,
        pcom_df,
        how = "outer",
        left_on = "hcl_key",
        right_on = "pcom_zie_mapper"
    )

    final_df["final_value"] = final_df.apply(
        lambda row: row["pcom_value"] if pd.notna(row["pcom_value"]) else row["hcl_value"],
        axis = 1 # Make sure for row wise operation. 
    )

    return final_df 



def write_answer(
    final_df: pd.DataFrame, 
    output_file: str = "zie_pcom_output.kmp"
) -> str:
    extension: str = ".kmp" if not output_file.endswith(".kmp") else ""
    final_path: str = f"{output_file}{extension}"
    with open(final_path, "w") as f:
        header: str = \
"""        [KeyRemap]
        """.replace(" ", "")
        key_value = (final_df["hcl_key"] + "=" + final_df["final_value"])\
                    .to_string(index = False).replace(" ","")
        
        f.write(header)
        f.write(key_value)
        print(f"Key mapped succesfully and stored in {final_path}")
        
        keymap = header + key_value

        return keymap


def main() -> None:

    st.set_page_config(
        page_title = "Automation by VRNeXGen",
        initial_sidebar_state = "auto"
    )

    st.header("VRX MigEmulator")
    st.sidebar.text("Automation is our AIM")
    keymap_tab, srl_sftl_tab,  = st.tabs(
        [
            "Key Mapping",
            "SRL -> SFTL",
        ]
    )

    with srl_sftl_tab:
        # st.text("Ahh, I'll add this tomorrow😁")

        uploaded_file = st.file_uploader("Upload your .srl file", type = ["srl"])
        if uploaded_file is not None:

            output_path = st.text_input("Output SFTL file path", value = "output.sftl")
            if output_path:
            # Read uploaded file as text
                srl_text = uploaded_file.read().decode("utf-8")
                srl_lines = srl_text.splitlines()

                st.subheader("SRL Content")
                # Wrap the content in expandable text area
                with st.expander("View SRL Lines"):
                    # Display the SRL lines in a text area
                    st.text_area("SRL Lines", value="\n".join(srl_lines), height=300)

                # Convert SRL to SFTL
                if st.button("Convert to SFTL"):
                    sftl_content = convert_srl_to_sftl(srl_lines)
                    write_sftl_to_file(sftl_content, output_path)
                    # st.markdown(f"<h2 style='color:green;'>Conversion successful! SFTL file saved as '{output_path}'.</h2>", unsafe_allow_html = True)
                    st.markdown(
                        f"<h2 style='color:#006400; background-color:white; padding:10px;'>Conversion successful! SFTL file saved as '{output_path}'.</h2>",
                        unsafe_allow_html=True
                    )

                    st.subheader("SFTL Content")
                    st.text_area("SFTL Output", value = sftl_content, height=300)


    with keymap_tab:
        
        pcom_file = st.file_uploader(label = "PCOM Keymap File", type = [".kmp"])
        output_file_name: str = st.text_input("Output filename", placeholder = "zie_keymap.kmp")
        if not output_file_name:
            output_file_name = "zie_keymap.kmp"
        if st.button("Convert Pcom to Zie KMP"):
            if pcom_file:
                with st.spinner("Key Mapping!"):
                    content_bytes = pcom_file.readlines()
                    content = [line.decode('utf-8').strip() for line in content_bytes]
                    print(content)
                    
                    pcom_df: pd.DataFrame = get_pcom_df(pcom_content = content)
                    final_df: pd.DataFrame = get_final_df(pcom_df)

                    keymap = write_answer(final_df, output_file_name)

                    # st.success("PCOMM .kmp file converted into ZIE .kmp file")
                    st.markdown(
                        f"<h4 style='color:#006400; background-color:white; padding:5pxpx;'>PCOMM .kmp file converted into ZIE .kmp file.</h4>",
                        unsafe_allow_html=True
                    )

                    with st.expander("View"):
                        st.text_area("KEYMAP",value = keymap, height=300)




if __name__ == "__main__":
    main()
