export const PRICING_DATA = [
    {
        title: 'FREE',
        price: '$0',
        period: null,
        subtitle: 'Perfect for casual use',
        features: [
            '10 Daily Conversions',
            '10MB Max File Size',
            'Basic Tools Access',
            'Standard Processing Speed',
            'Community Support'
        ],
        icon: 'fa-solid fa-bolt',
        color: '#A0AEC0',
        isPopular: false,
        planId: 'free',
        buttonText: 'Current Plan'
    },
    {
        title: 'MONTHLY PRO',
        price: '$9.99',
        period: '/month',
        subtitle: 'Ideal for power users',
        features: [
            'Unlimited Conversions',
            '100MB Max File Size',
            'Ad-Free Experience',
            'Priority Processing',
            'All Premium Tools',
            'Email Support'
        ],
        icon: 'fa-solid fa-wand-magic-sparkles',
        color: '#448aff',
        isPopular: true,
        planId: 'monthly',
        buttonText: 'Choose Plan',
        stripePlanType: 'monthly'
    },
    {
        title: 'YEARLY PRO',
        price: '$99',
        period: '/year',
        subtitle: 'Best value - Save $20!',
        features: [
            'Unlimited Conversions',
            '500MB Max File Size',
            'Ad-Free Experience',
            'VIP Priority Processing',
            'All Premium Tools',
            'Priority Email Support',
            'API Access (Coming Soon)'
        ],
        icon: 'fa-solid fa-crown',
        color: '#00c853',
        isPopular: false,
        planId: 'yearly',
        buttonText: 'Choose Plan',
        stripePlanType: 'yearly',
        badge: 'SAVE 17%'
    }
];
