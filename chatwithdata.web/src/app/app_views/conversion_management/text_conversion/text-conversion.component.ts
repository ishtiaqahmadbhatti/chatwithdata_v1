import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { TEXT_CONVERSION_TOOLS } from '../../../app_data/text-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-text-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './text-conversion.component.html',
    styleUrl: './text-conversion.component.css'
})
export class TextConversionComponent {
    tools: ConversionTool[] = TEXT_CONVERSION_TOOLS;
}
