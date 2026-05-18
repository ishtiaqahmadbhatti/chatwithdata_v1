import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PDF_CONVERSION_TOOLS } from '../../../app_data/pdf-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-pdf-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './pdf-conversion.component.html',
    styleUrl: './pdf-conversion.component.css'
})
export class PdfConversionComponent {
    pdfconversiontools: ConversionTool[] = PDF_CONVERSION_TOOLS;
}
