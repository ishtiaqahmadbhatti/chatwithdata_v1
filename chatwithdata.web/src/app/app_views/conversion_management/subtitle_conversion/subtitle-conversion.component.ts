import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SUBTITLE_CONVERSION_TOOLS } from '../../../app_data/subtitle-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-subtitle-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './subtitle-conversion.component.html',
    styleUrl: './subtitle-conversion.component.css'
})
export class SubtitleConversionComponent {
    tools: ConversionTool[] = SUBTITLE_CONVERSION_TOOLS;
}
