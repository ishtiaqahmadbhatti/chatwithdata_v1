import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { EBOOK_CONVERSION_TOOLS } from '../../../app_data/ebook-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-ebook-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './ebook-conversion.component.html',
    styleUrl: './ebook-conversion.component.css'
})
export class EbookConversionComponent {
    tools: ConversionTool[] = EBOOK_CONVERSION_TOOLS;
}
