import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { VIDEO_CONVERSION_TOOLS } from '../../../app_data/video-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-video-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './video-conversion.component.html',
    styleUrl: './video-conversion.component.css'
})
export class VideoConversionComponent {
    tools: ConversionTool[] = VIDEO_CONVERSION_TOOLS;
}
