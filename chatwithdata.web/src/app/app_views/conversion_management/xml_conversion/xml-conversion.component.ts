import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { XML_CONVERSION_TOOLS } from '../../../app_data/xml-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-xml-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './xml-conversion.component.html',
    styleUrl: './xml-conversion.component.css'
})
export class XmlConversionComponent {
    tools: ConversionTool[] = XML_CONVERSION_TOOLS;
}
