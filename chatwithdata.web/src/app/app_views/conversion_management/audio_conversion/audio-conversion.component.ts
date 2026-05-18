import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AUDIO_CONVERSION_TOOLS } from '../../../app_data/audio-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-audio-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './audio-conversion.component.html',
    styleUrl: './audio-conversion.component.css'
})
export class AudioConversionComponent {
    tools: ConversionTool[] = AUDIO_CONVERSION_TOOLS;
}
