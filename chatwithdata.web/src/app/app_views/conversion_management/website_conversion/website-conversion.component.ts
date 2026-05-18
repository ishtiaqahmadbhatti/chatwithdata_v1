import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { WEBSITE_CONVERSION_TOOLS } from '../../../app_data/website-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-website-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './website-conversion.component.html',
    styleUrl: './website-conversion.component.css'
})
export class WebsiteConversionComponent {
    tools: ConversionTool[] = WEBSITE_CONVERSION_TOOLS;
}
