import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { OCR_CONVERSION_TOOLS } from '../../../app_data/ocr-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-ocr-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './ocr-conversion.component.html',
    styleUrl: './ocr-conversion.component.css'
})
export class OcrConversionComponent {
    tools: ConversionTool[] = OCR_CONVERSION_TOOLS;
}
