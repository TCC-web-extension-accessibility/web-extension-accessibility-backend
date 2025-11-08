from pydantic import BaseModel


class FeatureControl(BaseModel):
    enabled: bool


class WidgetControls(BaseModel):
    contrast: FeatureControl
    reader: FeatureControl
    font_size: FeatureControl
    font_family: FeatureControl
    line_height: FeatureControl
    letter_spacing: FeatureControl
    disable_animations: FeatureControl
    hide_images: FeatureControl
    reading_guide: FeatureControl
    voice_navigation: FeatureControl
    highlight_links: FeatureControl
    saturation: FeatureControl
    color_filter: FeatureControl


class WidgetFeatures(BaseModel):
    language_selector: FeatureControl
    accessibility_profiles: FeatureControl
    widget_controls: WidgetControls


class WidgetConfigJson(BaseModel):
    features: WidgetFeatures


class DeploymentInfo(BaseModel):
    status: str
    environment: str
    workflow: str


class WidgetConfigAdminResponse(BaseModel):
    id: int
    version: str
    config: WidgetConfigJson
    deployment_status: str

    class Config:
        populate_by_name = True
        from_attributes = True


class WidgetConfigUpdateResponse(BaseModel):
    message: str
    config: WidgetConfigJson
    deployment: DeploymentInfo


class WidgetConfigPublicResponse(BaseModel):
    version: str
    features: WidgetFeatures


class DeploymentStatusResponse(BaseModel):
    status: str
    conclusion: str | None = None
    url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class WidgetConfigUpdateRequest(BaseModel):
    features: WidgetFeatures
    version: str | None = None

