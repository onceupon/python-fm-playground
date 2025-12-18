export const defaultModel = {
    modelName: "Anthropic Claude 3.5 Sonnet",
    modelId: "anthropic.claude-3-5-sonnet-20241022-v2:0",
    temperatureRange: {
        min: 0,
        max: 1,
        default: 0.5
    },
    maxTokenRange: {
        min: 0,
        max: 4096,
        default: 200
    }
}

export const models = [
    defaultModel,
    {
        modelName: "AI21 Labs Jurassic-2",
        modelId: "ai21.j2-mid-v1",
        temperatureRange: {
            min: 0,
            max: 1,
            default: 0.5
        },
        maxTokenRange: {
            min: 0,
            max: 8191,
            default: 200
        }
    }
]

export const defaultPayload = {
    prompt: "", 
    temperature: defaultModel.temperatureRange.default,
    maxTokens: defaultModel.maxTokenRange.default
}