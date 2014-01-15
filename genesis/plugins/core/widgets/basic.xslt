<xsl:template match="label">
    <span class="ui-el-label-{x:attr(@size, '1')} {@class}" style="{x:iif(@bold, 'font-weight: bold;', '')} {x:iif(@monospace, 'font-family: monospace;', '')} {x:iif(@lbreak, 'max-width: 500px;', '')}">
        <xsl:value-of select="@text" />
    </span>
</xsl:template>


<xsl:template match="image">
    <img class="ui-el-image" src="{@file}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};" />
</xsl:template>


<xsl:template match="toolbar">
    <xsl:apply-templates />
    <hr />
</xsl:template>

<!-- Button magic -->
<xsl:template match="buttongroup">
    <div class="btn-group">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="button">
    <xsl:variable name="onclickjs">
        <xsl:choose>
            <xsl:when test="@warning != ''">
                return Genesis.showWarning('<xsl:value-of select="@warning"/>',
                    '<xsl:value-of select="@id"/>'<xsl:choose><xsl:when test="@cls != ''">,
                    '<xsl:value-of select="@cls"/>'</xsl:when></xsl:choose>);
            </xsl:when>

            <xsl:when test="@onclick = 'form'">
                <xsl:choose>
                    <xsl:when test="@mp != ''">
                        return Genesis.submit('<xsl:value-of select="@form" />', '<xsl:value-of select="@action" />', true, <xsl:value-of select="@modal" />);
                    </xsl:when>
                    <xsl:otherwise>
                        return Genesis.submit('<xsl:value-of select="@form" />', '<xsl:value-of select="@action" />', null, <xsl:value-of select="x:attr(@modal, 'false')" />);
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>

            <xsl:when test="@onclick = '' or not (@onclick)">
                <xsl:variable name="cls">
                    <xsl:choose>
                        <xsl:when test="@cls != ''">
                            <xsl:value-of select="@cls" />
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="x:attr(@class, 'button')" />
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                return Genesis.query('/handle/<xsl:value-of
                        select="$cls" />/click/<xsl:value-of
                        select="@id" />');
            </xsl:when>

            <xsl:otherwise>
                <xsl:value-of select="@onclick" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:variable name="design">
        <xsl:choose>
            <xsl:when test="@design != ''">
                <xsl:value-of select="@design" />
            </xsl:when>
            <xsl:otherwise>default</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:variable name="size">
        <xsl:choose>
            <xsl:when test="@size != ''">
                <xsl:value-of select="@size" />
            </xsl:when>
            <xsl:otherwise>sm</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <a href="{@href}" onclick="{$onclickjs}" class="btn btn-{$design} btn-{$size}">
        <xsl:choose>
            <xsl:when test="@iconfont != ''">
                <i class="{@iconfont}"></i>
                <xsl:if test="@text">
                    &#160;<xsl:value-of select="@text" />
                </xsl:if>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="@text" />
            </xsl:otherwise>
        </xsl:choose>
    </a>
</xsl:template>

<!-- End of button magic -->



<xsl:template match="linklabel">
    <a href="#" onclick="javascript:return Genesis.query('/handle/linklabel/click/{@id}');" class="ui-el-link" style="{x:iif(@bold, 'font-weight: bold;', '')}">
        <xsl:if test="@iconfont">
            <i class="{@iconfont}"></i>&#160;
        </xsl:if>
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="outlinklabel">
    <a href="{@url}" target="blank" class="ui-el-link">
        <xsl:if test="@iconfont">
            <i class="{@iconfont}"></i>&#160;
        </xsl:if>
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="progressbar">
    <div class="ui-el-progressbar-wrapper">
        <div style="width:{@left}px" class="ui-el-progressbar-active">
            <div><div/></div>
        </div>
        <div style="width:{@right}px" class="ui-el-progressbar" />
    </div>
</xsl:template>

<xsl:template match="elementbox">
    <div class="ui-el-elementbox">
        <xsl:apply-templates />
    </div>
</xsl:template>





<xsl:template match="tooltip">
    <xsl:variable name="id" select="x:id(@id)" />
    <div style="display:inline-block; {@styles}" id="{$id}">
        <xsl:apply-templates />
    </div>
    <script>
        $('#<xsl:value-of select="$id" />').twipsy({
            animate: true,
            placement: '<xsl:value-of select="x:attr(@placement, 'right')" />',
            html: true,
            live: true,
            delayIn: <xsl:value-of select="x:attr(@delay, '0')" />,
            offset: <xsl:value-of select="x:attr(@offset, '0')" />,
            title: '<xsl:value-of select="x:jsesc(x:attr(@text, ''))" />',
            trigger: '<xsl:value-of select="x:attr(@trigger, 'hover')" />',
        });
    </script>
</xsl:template>

<xsl:template match="popover">
    <xsl:variable name="id" select="x:id(@id)" />
    <a id="{$id}" style="display:inline-block; {@styles}" class="pop-trigger {@class}" onclick="Genesis.UI.prepPopover(event, '{@id}');{@onclick}">
        <xsl:apply-templates />
    </a>
    <script>
        $('#<xsl:value-of select="$id" />').popover({
            animation: true,
            placement: '<xsl:value-of select="x:attr(@placement, 'right')" />',
            html: true,
            delayIn: <xsl:value-of select="x:attr(@delay, '0')" />,
            offset: <xsl:value-of select="x:attr(@offset, '0')" />,
            title: function() {
              return $("#<xsl:value-of select="$id" />-head").html();
            },
            content: function() {
              return $("#<xsl:value-of select="$id" />-content").html();
            },
            trigger: '<xsl:value-of select="x:attr(@trigger, 'click')" />',
        });
    </script>
</xsl:template>


<xsl:template match="icon">
    <tooltip placement="above" text="{@text}"><image id="{@id}" file="{@icon}"/></tooltip>
</xsl:template>

<xsl:template match="iconfont">
    <tooltip placement="above" text="{@text}"><i class="{@iconfont}"></i></tooltip>
</xsl:template>

<xsl:template match="tipicon">
    <tooltip placement="above" text="{@text}"><button id="{@id}" design="tipicon" cls="{@cls}" onclick="{@onclick}" warning="{@warning}" iconfont="{@iconfont}"/></tooltip>
</xsl:template>
