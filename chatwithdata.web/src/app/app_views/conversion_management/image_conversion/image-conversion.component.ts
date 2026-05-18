import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { IMAGE_CONVERSION_TOOLS } from '../../../app_data/image-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-image-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './image-conversion.component.html',
    styleUrl: './image-conversion.component.css'
})
export class ImageConversionComponent {
    tools: ConversionTool[] = IMAGE_CONVERSION_TOOLS;
}
