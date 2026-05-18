import { Component, EventEmitter, Input, Output, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';

// Import tool data for category lookup
import { PDF_CONVERSION_TOOLS } from '../../app_data/pdf-conversion-tools.data';
import { IMAGE_CONVERSION_TOOLS } from '../../app_data/image-conversion-tools.data';
import { AUDIO_CONVERSION_TOOLS } from '../../app_data/audio-conversion-tools.data';
import { VIDEO_CONVERSION_TOOLS } from '../../app_data/video-conversion-tools.data';
import { OFFICE_CONVERSION_TOOLS } from '../../app_data/office-conversion-tools.data';
import { EBOOK_CONVERSION_TOOLS } from '../../app_data/ebook-conversion-tools.data';
import { JSON_CONVERSION_TOOLS } from '../../app_data/json-conversion-tools.data';
import { XML_CONVERSION_TOOLS } from '../../app_data/xml-conversion-tools.data';
import { CSV_CONVERSION_TOOLS } from '../../app_data/csv-conversion-tools.data';
import { TEXT_CONVERSION_TOOLS } from '../../app_data/text-conversion-tools.data';
import { OCR_CONVERSION_TOOLS } from '../../app_data/ocr-conversion-tools.data';
import { WEBSITE_CONVERSION_TOOLS } from '../../app_data/website-conversion-tools.data';
import { SUBTITLE_CONVERSION_TOOLS } from '../../app_data/subtitle-conversion-tools.data';
import { FILE_FORMATTER_TOOLS } from '../../app_data/file-formatter-tools.data';
import { MARKDOWN_CONVERSION_TOOLS } from '../../app_data/markdown-conversion-tools.data';
import { SoundService } from '../../app_services/sound.service';

@Component({
    selector: 'app-file-conversion-ui',
    standalone: true,
    imports: [CommonModule, RouterLink],
    templateUrl: './file-conversion-ui.component.html',
    styleUrl: './file-conversion-ui.component.css'
})
export class FileConversionUiComponent implements OnInit, OnChanges {
    @Input() title: string = '';
    @Input() description: string = '';
    @Input() sourceIcon: string = 'fas fa-file';
    @Input() targetIcon: string = 'fas fa-file-alt';

    @Input() allowedExtensions: string = '*';
    @Input() allowedExtensionsText: string = '';
    @Input() convertButtonText: string = 'Convert';

    @Input() selectedFile: File | null = null;
    @Input() isConverting: boolean = false;
    @Input() conversionStatus: string = '';
    @Input() uploadProgress: number = 0;

    @Input() conversionResult: { downloadUrl: string, fileName: string } | null = null;
    @Input() disableFileUpload: boolean = false;
    @Input() keepContentVisible: boolean = false;

    @Output() fileSelected = new EventEmitter<File>();
    @Output() convert = new EventEmitter<void>();
    @Output() reset = new EventEmitter<void>();
    @Output() download = new EventEmitter<void>();
    
    constructor(private router: Router, private soundService: SoundService) {}

    ngOnChanges(changes: SimpleChanges) {
        // Success Sound: When conversionResult changes from null to a value
        if (changes['conversionResult'] && changes['conversionResult'].currentValue && !changes['conversionResult'].previousValue) {
            this.soundService.playSuccess();
        }

        // Error Sound: When conversionStatus indicates failure (emoji, 'fail', or 'error')
        if (changes['conversionStatus']) {
            const status = (changes['conversionStatus'].currentValue || '').toLowerCase();
            const prevStatus = (changes['conversionStatus'].previousValue || '').toLowerCase();
            
            const isError = status.includes('❌') || status.includes('fail') || status.includes('error');
            const wasError = prevStatus.includes('❌') || prevStatus.includes('fail') || prevStatus.includes('error');
            
            if (isError && !wasError) {
                this.soundService.playError();
            }
        }
    }

    currentCategory: string = '';

    ngOnInit() {
        this.currentCategory = this.findCategoryForTool(this.title);
    }

    findCategoryForTool(toolTitle: string): string {
        // Map must match ToolFeedbackComponent category names exactly
        const categories = [
            { name: 'PDF Conversion', tools: PDF_CONVERSION_TOOLS },
            { name: 'Image Conversion', tools: IMAGE_CONVERSION_TOOLS },
            { name: 'Audio Conversion', tools: AUDIO_CONVERSION_TOOLS },
            { name: 'Video Conversion', tools: VIDEO_CONVERSION_TOOLS },
            { name: 'Office Conversion', tools: OFFICE_CONVERSION_TOOLS },
            { name: 'E-Book Conversion', tools: EBOOK_CONVERSION_TOOLS },
            { name: 'JSON Conversion', tools: JSON_CONVERSION_TOOLS },
            { name: 'XML Conversion', tools: XML_CONVERSION_TOOLS },
            { name: 'CSV Conversion', tools: CSV_CONVERSION_TOOLS },
            { name: 'Text Conversion', tools: TEXT_CONVERSION_TOOLS },
            { name: 'OCR Conversion', tools: OCR_CONVERSION_TOOLS },
            { name: 'Website Conversion', tools: WEBSITE_CONVERSION_TOOLS },
            { name: 'Subtitle Conversion', tools: SUBTITLE_CONVERSION_TOOLS },
            { name: 'File Formatter', tools: FILE_FORMATTER_TOOLS },
            { name: 'Markdown Conversion', tools: MARKDOWN_CONVERSION_TOOLS }
        ];

        const currentUrl = this.router.url;

        // Try to match by title AND current route first (for disambiguation)
        for (const cat of categories) {
            if (cat.tools.some(t => t.title === toolTitle && t.route && currentUrl.includes(t.route))) {
                return cat.name;
            }
        }

        // Fallback: match by title only
        for (const cat of categories) {
            if (cat.tools.some(t => t.title === toolTitle)) {
                return cat.name;
            }
        }
        return '';
    }

    onFileChange(event: any): void {
        const file = event.target.files[0];
        if (file) {
            this.fileSelected.emit(file);
        }
    }
}
