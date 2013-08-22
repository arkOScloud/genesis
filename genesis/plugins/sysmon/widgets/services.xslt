<xsl:template match="servicepluginpanel">
    <div class="ui-el-toolbar ui-service-bar" style="float:right;">
        <xsl:choose>
            <xsl:when test="@alert = 'True'">
                <button class="servicecontrol" text="Status" design="danger" id="services" iconfont="gen-list" style="float:right;" />
            </xsl:when>
            <xsl:when test="@alert = 'False'">
                <button class="servicecontrol" text="Status" id="services" iconfont="gen-list" style="float:right;" />
            </xsl:when>
        </xsl:choose>
    </div>
</xsl:template>
