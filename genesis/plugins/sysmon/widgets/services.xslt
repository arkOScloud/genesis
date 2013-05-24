<xsl:template match="servicepluginpanel">
    <div class="ui-el-toolbar ui-service-bar">
        <xsl:choose>
            <xsl:when test="@status = 'running'">
                <div class="ui-service-status-box">
                    <label text="Running"/>
                </div>
                <button class="servicecontrol" text="Restart" id="restart" iconfont="gen-loop" /><button class="servicecontrol" text="Stop" id="stop" iconfont="gen-stop" />
            </xsl:when>
            <xsl:when test="@status = 'stopped'">
                <div class="ui-service-status-box">
                    <label text="Stopped"/>
                </div>
                <button class="servicecontrol" text="Start" id="start" iconfont="gen-play-2" />
            </xsl:when>
            <xsl:when test="@status = 'failed'">
                <div class="ui-service-status-box">
                    <i class="gen-minus-circle"></i>
                    &#160;<label text="Failed to start"/>
                </div>
                <button class="servicecontrol" text="Restart" id="restart" iconfont="gen-loop"/>
            </xsl:when>
        </xsl:choose>
    </div>
</xsl:template>
