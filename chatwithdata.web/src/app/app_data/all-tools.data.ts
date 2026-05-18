import { ConversionTool } from '../app_models/conversion-tool.model';
import { PDF_CONVERSION_TOOLS } from './pdf-conversion-tools.data';
import { IMAGE_CONVERSION_TOOLS } from './image-conversion-tools.data';
import { AUDIO_CONVERSION_TOOLS } from './audio-conversion-tools.data';
import { VIDEO_CONVERSION_TOOLS } from './video-conversion-tools.data';
import { OFFICE_CONVERSION_TOOLS } from './office-conversion-tools.data';
import { EBOOK_CONVERSION_TOOLS } from './ebook-conversion-tools.data';
import { JSON_CONVERSION_TOOLS } from './json-conversion-tools.data';
import { XML_CONVERSION_TOOLS } from './xml-conversion-tools.data';
import { CSV_CONVERSION_TOOLS } from './csv-conversion-tools.data';
import { TEXT_CONVERSION_TOOLS } from './text-conversion-tools.data';
import { OCR_CONVERSION_TOOLS } from './ocr-conversion-tools.data';
import { WEBSITE_CONVERSION_TOOLS } from './website-conversion-tools.data';
import { SUBTITLE_CONVERSION_TOOLS } from './subtitle-conversion-tools.data';
import { FILE_FORMATTER_TOOLS } from './file-formatter-tools.data';
import { MARKDOWN_CONVERSION_TOOLS } from './markdown-conversion-tools.data';

export interface SearchableTool extends ConversionTool {
    categoryName: string;
}

export const ALL_TOOLS: SearchableTool[] = [
    ...PDF_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'PDF Conversion' })),
    ...IMAGE_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'Image Conversion' })),
    ...AUDIO_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'Audio Conversion' })),
    ...VIDEO_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'Video Conversion' })),
    ...OFFICE_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'Office Conversion' })),
    ...EBOOK_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'E-Book Conversion' })),
    ...JSON_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'JSON Conversion' })),
    ...XML_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'XML Conversion' })),
    ...CSV_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'CSV Conversion' })),
    ...TEXT_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'Text Conversion' })),
    ...OCR_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'OCR Conversion' })),
    ...WEBSITE_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'Website Conversion' })),
    ...SUBTITLE_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'Subtitle Conversion' })),
    ...FILE_FORMATTER_TOOLS.map(t => ({ ...t, categoryName: 'File Formatter' })),
    ...MARKDOWN_CONVERSION_TOOLS.map(t => ({ ...t, categoryName: 'Markdown Conversion' })),
];
