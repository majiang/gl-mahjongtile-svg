import logging
import os

from fontTools.ttLib import TTFont

logger = logging.getLogger(__name__)

def woff_to_svg(woff_file_path, output_directory):
    # WOFFファイルを読み込む
    font = TTFont(woff_file_path)
    logger.info(font.keys())
    
    # WOFFファイルからSVGフォントテーブルを抽出する
    svg_table = font["SVG "]
    
    # グリフのデータをSVGとして出力する
    for (glyph_name, glyph_data) in zip(font.getGlyphOrder(), svg_table.docList):
        file_name = f"{glyph_name}.svg"
        output_file_path = os.path.join(output_directory, file_name)
        with open(output_file_path, "w") as svg_file:
            svg_file.write(glyph_data.data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    woff_file_path = "original/GL-MahjongTile-Clr.woff"
    output_directory = "original/woff-svg"
    woff_to_svg(woff_file_path, output_directory)
