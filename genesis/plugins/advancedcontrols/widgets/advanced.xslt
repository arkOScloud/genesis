
<xsl:template match="codeinputarea">
            <xsl:if test="@help and (@help != '')">
                <helpicon text="{@help}"/>
            </xsl:if>
            <textarea class="ui-el-textarea" name="{@name}" id="{@id}">
                <xsl:if test="@disabled = 'True'">
                    <xsl:attribute name="disabled"/>
                </xsl:if>
            </textarea>
            <script>
                <xsl:choose>
                    <xsl:when test="@nodecode = 'True'">
                        ui_fill_custom_html('<xsl:value-of select="@id"/>', '<xsl:value-of select="@value"/>');
                    </xsl:when>
                    <xsl:otherwise>
                        ui_fill_custom_html('<xsl:value-of select="@id"/>', '<xsl:value-of select="x:b64(@value)"/>');
                    </xsl:otherwise>
                </xsl:choose>
                var cm = CodeMirror.fromTextArea(
                    $('#<xsl:value-of select="@id"/>')[0],
                    {
                        theme: 'default',
                        lineNumbers: true
                    }
                );
                cm.setSize('<xsl:value-of select="x:css(@width, '200')"/>', '<xsl:value-of select="x:css(@height, '200')"/>')
                $('#<xsl:value-of select="@id"/>')[0].editor = cm;
                cm.on('blur', function() {
                    cm.save();
                });
            </script>
</xsl:template>
