/**
 * Property Template Types and Configurations
 * Supports different property types with pre-configured templates
 */

import { RenovationStatus } from './property';

export interface PropertyTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'residential' | 'commercial' | 'mixed-use' | 'retail';
  
  // Default configuration values
  defaultConfig: {
    residential_units?: {
      total_units: number;
      average_rent_per_unit: number;
      average_square_feet_per_unit: number;
    };
    commercial_units?: {
      total_units: number;
      average_rent_per_unit: number;
      average_square_feet_per_unit: number;
    };
    renovation_info: {
      status: RenovationStatus;
      anticipated_duration_months: number;
      estimated_cost: number;
    };
    equity_structure: {
      investor_equity_share_pct: number;
      self_cash_percentage: number;
    };
  };
  
  // Fields to show/hide in the form
  formConfig: {
    showCommercialUnits: boolean;
    showResidentialUnits: boolean;
    requiredFields: string[];
    optionalFields: string[];
  };
}

export const PROPERTY_TEMPLATES: PropertyTemplate[] = [
  {
    id: 'multifamily-residential',
    name: 'Multifamily Residential',
    description: 'Apartment buildings, condos, and residential complexes',
    icon: '🏢',
    category: 'residential',
    defaultConfig: {
      residential_units: {
        total_units: 12,
        average_rent_per_unit: 2500,
        average_square_feet_per_unit: 850
      },
      renovation_info: {
        status: RenovationStatus.PLANNED,
        anticipated_duration_months: 6,
        estimated_cost: 150000
      },
      equity_structure: {
        investor_equity_share_pct: 25,
        self_cash_percentage: 80
      }
    },
    formConfig: {
      showCommercialUnits: false,
      showResidentialUnits: true,
      requiredFields: ['property_name', 'residential_units', 'renovation_info', 'equity_structure'],
      optionalFields: ['commercial_units', 'purchase_price', 'property_address', 'notes']
    }
  },
  {
    id: 'commercial-office',
    name: 'Commercial Office',
    description: 'Office buildings and business centers',
    icon: '🏪',
    category: 'commercial',
    defaultConfig: {
      commercial_units: {
        total_units: 8,
        average_rent_per_unit: 42000,
        average_square_feet_per_unit: 1200
      },
      renovation_info: {
        status: RenovationStatus.PLANNED,
        anticipated_duration_months: 4,
        estimated_cost: 100000
      },
      equity_structure: {
        investor_equity_share_pct: 30,
        self_cash_percentage: 75
      }
    },
    formConfig: {
      showCommercialUnits: true,
      showResidentialUnits: false,
      requiredFields: ['property_name', 'commercial_units', 'renovation_info', 'equity_structure'],
      optionalFields: ['residential_units', 'purchase_price', 'property_address', 'notes']
    }
  },
  {
    id: 'mixed-use',
    name: 'Mixed-Use Property',
    description: 'Residential units with ground-floor commercial space',
    icon: '🏬',
    category: 'mixed-use',
    defaultConfig: {
      residential_units: {
        total_units: 8,
        average_rent_per_unit: 2200,
        average_square_feet_per_unit: 750
      },
      commercial_units: {
        total_units: 3,
        average_rent_per_unit: 22400,
        average_square_feet_per_unit: 800
      },
      renovation_info: {
        status: RenovationStatus.PLANNED,
        anticipated_duration_months: 8,
        estimated_cost: 180000
      },
      equity_structure: {
        investor_equity_share_pct: 25,
        self_cash_percentage: 85
      }
    },
    formConfig: {
      showCommercialUnits: true,
      showResidentialUnits: true,
      requiredFields: ['property_name', 'residential_units', 'commercial_units', 'renovation_info', 'equity_structure'],
      optionalFields: ['purchase_price', 'property_address', 'notes']
    }
  },
  {
    id: 'retail-shopping',
    name: 'Retail & Shopping',
    description: 'Strip malls, shopping centers, and retail spaces',
    icon: '🛍️',
    category: 'retail',
    defaultConfig: {
      commercial_units: {
        total_units: 6,
        average_rent_per_unit: 37500,
        average_square_feet_per_unit: 1500
      },
      renovation_info: {
        status: RenovationStatus.PLANNED,
        anticipated_duration_months: 3,
        estimated_cost: 120000
      },
      equity_structure: {
        investor_equity_share_pct: 35,
        self_cash_percentage: 70
      }
    },
    formConfig: {
      showCommercialUnits: true,
      showResidentialUnits: false,
      requiredFields: ['property_name', 'commercial_units', 'renovation_info', 'equity_structure'],
      optionalFields: ['residential_units', 'purchase_price', 'property_address', 'notes']
    }
  }
];

export function getTemplateById(templateId: string): PropertyTemplate | undefined {
  return PROPERTY_TEMPLATES.find(template => template.id === templateId);
}

export function getTemplatesByCategory(category: PropertyTemplate['category']): PropertyTemplate[] {
  return PROPERTY_TEMPLATES.filter(template => template.category === category);
}