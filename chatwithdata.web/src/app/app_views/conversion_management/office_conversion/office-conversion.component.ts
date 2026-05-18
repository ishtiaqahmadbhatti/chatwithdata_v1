import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { OFFICE_CONVERSION_TOOLS } from '../../../app_data/office-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-office-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './office-conversion.component.html',
    styleUrl: './office-conversion.component.css'
})
export class OfficeConversionComponent {
    tools: ConversionTool[] = OFFICE_CONVERSION_TOOLS;
}
